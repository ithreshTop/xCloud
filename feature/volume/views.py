#!/usr/bin/env python
# coding:utf-8
import datetime, pytz
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from feature.util import nova_token, cinder_token, keystone_token, cinder_admin_token, set_dc
from feature.volume.models import Volume as volume_model
from feature.volume.models import VolumeToServer as vs
from feature.serverlist.models import MetringGroup as mg
import json
import logging
LOG = logging.getLogger('feature')
BUG = logging.getLogger('request')


# 磁盘展示页面
@login_required
def volume(request):
    user = request.user
    if user.username == 'admin':
        return HttpResponseRedirect("/logout/")
    volumeToServer = {}
    novas = []
    cinders = []
    types = ["experiment"]
    for ty_pe in types:
        udc = set_dc(ty_pe)
        cinder = cinder_token(user, udc)
        if request.is_ajax():
            volume_name = request.POST.get("volumename", None)
            status = 0
            if volume_name is not None:
                try:
                    cinder.volumes.find(display_name=volume_name)
                    status = 1
                except:
                    status = 0
            return HttpResponse(status)
        volume = {}
        ins = {}
        ins[ty_pe] = {}
        volume[ty_pe] = {}
        nova = nova_token(user, udc)
        volume[ty_pe] = cinder.volumes.list()
        ins[ty_pe] = nova.servers.list()
        for v in cinder.volumes.list():
            if vs.objects.filter(volume_id=v.id):
                volumeToServer[v.id] = vs.objects.get(volume_id=v.id).server_id
        cinders.append(volume)
        novas.append(ins)

    return render_to_response('pages/volume/volume.html', {'current_user': user,
                                                           'vols': cinders,
                                                           'servers': novas,
                                                           'vts': volumeToServer,
                                                           'metering_group': mg.objects.all(),
                                                           'local_vols': volume_model.objects.filter(deleted_date=None)
                                                           })

'''
def volume_create(request):
    user = request.user
    return render_to_response('pages/volume/create.html', {'current_user': user})
'''

# 创建磁盘
def volume_create_acc(request):
    user = request.user
    dc = request.POST.get('type')
    udc = set_dc(dc)
    volume_name = request.POST.get('volume_name_create')
    size = int(request.POST.get('getSize'))
    description = request.POST.get('description')
    group_name = request.POST.get('group')
    volume_inuse = 0
    keystone = keystone_token(user, udc)
    cinder = cinder_token(user, udc)
    cinder_admin = cinder_admin_token(udc)
    volume_sum = cinder_admin.quotas.get(keystone.tenant_id)
    # 取出已经使用的磁盘大小
    for vol in cinder.volumes.list():
        volume_inuse += cinder.volumes.get(vol.id).size
    # 与配额进行比较
    if (size+volume_inuse) > volume_sum.gigabytes:
        message = "超出配额，如需扩展请发送邮件申请！"
        BUG.error("User %s volume quotas:%s has been used up" % (user.username, volume_sum.gigabytes))
        return render_to_response('base.html', {"error_message": message,
                                               "current_user": user})
    else:
        # 先创建磁盘，再在本地数据库中同步。
        volume_ins = cinder.volumes.create(display_name=volume_name,
                                           size=size,
                                           display_description=description)
        group = mg.objects.get(group_name=group_name)
        volume_model.objects.create(
            name=volume_name,
            volume_id=volume_ins.id,
            size=size,
            # create_date = volume_ins.created_at,
            create_date=datetime.datetime.now(pytz.utc),
            description=description,
            type=dc,
            user=user,
            metering_group=group,
        )
    LOG.info("User %s created volume name: %s,size: %s." % (user.username, volume_name, size))
    return HttpResponseRedirect('/feature/volume/')



# 绑定
def load(request):
    try:
        user = request.user
        dc = request.POST.get("server").split("|")[1]
        volume_id = request.POST.get("volume_id")
        host_id = request.POST.get("server").split("|")[0]
        udc = set_dc(dc)
        cinder = cinder_token(user, udc)
        nova = nova_token(user, udc)
        host = nova.servers.get(host_id)
        vol = cinder.volumes.get(volume_id)
        status = cinder.volumes.get(volume_id).status
        if("in-use" == status):
            mess = "已经挂载的磁盘不能进行挂载！"
            return render_to_response('base.html',{"error_message":mess,"current_user": user})
        # host = nova.servers.find(name=host_name)
        cinder.volumes.attach(volume_id, host_id, mountpoint='/dev/vdc', mode='rw')
        vs.objects.create(server_id=host_id, volume_id=volume_id,)
        LOG.info("User %s attached volume name: %s,to: %s." % (user.username, vol.display_name, host.name))
        return HttpResponseRedirect('/feature/volume/')
    except Exception as e:
        LOG.error("User %s attach volume error! message:[%s]"% (user.username,e))
        message = "挂载磁盘错误，请稍后重新创建或联系管理员"
        return render_to_response('base.html', {"error_message": message,
                                                   "current_user": user})

# 解绑
def unload(request, vol_id, dc):
    LOG.info("reviced param: volume id %s", vol_id)
    user = request.user
    udc = set_dc(dc)
    cinder = cinder_token(user, udc)
    cinder.volumes.detach(vol_id)
    vs.objects.filter(volume_id=vol_id).delete()
    volume_name = cinder.volumes.get(vol_id).display_name
    LOG.info("User %s detached volume name: %s." % (user.username, volume_name))
    return HttpResponseRedirect("/feature/volume/")

# 扩展容量
def extend(request):
    user = request.user
    dc = request.POST.get("vol_type").split(",")[0]
    vol_id = request.POST.get("vol_type").split(",")[1]
    re_size = int(request.POST.get('re_size'))
    udc = set_dc(dc)
    volume_inuse = 0
    keystone = keystone_token(user, udc)
    cinder = cinder_token(user, udc)
    status = cinder.volumes.get(vol_id).status
    now_size = cinder.volumes.get(vol_id).size
    if(status=="in-use"):
        mess = "已经挂载的磁盘不能进行扩展！"
        return render_to_response('base.html',{"error_message":mess,"current_user": user})
    cinder_admin = cinder_admin_token(udc)
    volume_sum = cinder_admin.quotas.get(keystone.tenant_id)
    # 取出已经使用的磁盘大小
    for vol in cinder.volumes.list():
        volume_inuse += cinder.volumes.get(vol.id).size
    # 与配额进行比较
    count_sum = volume_sum.gigabytes
    if (re_size+volume_inuse-now_size) > count_sum:
        message = "超出配额，如需扩展请发送邮件申请！"
        BUG.error("User %s volume quotas:%s has been used up" % (user.username, volume_sum.gigabytes))
        return render_to_response('base.html', {"error_message": message,
                                               "current_user": user})
    else:
        # 先扩展磁盘，再在本地数据库中同步。
        vol = cinder.volumes.get(vol_id)
        cinder.volumes.extend(vol_id, re_size)
        # 根据id取出磁盘，如果删除时间为空，就更新该条数据的删除时间。
        volume_select = volume_model.objects.filter(volume_id=vol_id).filter(deleted_date=None)
        metering_group_id = volume_select[0].metering_group_id
        ty_pe = volume_select[0].type
        volume_select.update(
            # deleted_date =time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
            deleted_date=datetime.datetime.now(pytz.utc)
            )
        # 再创建一条新的磁盘数据，其删除时间为空，
        volume_model.objects.create(
            name=vol.display_name,
            volume_id=vol_id,
            size=re_size,
            # create_date = volume_ins.created_at,
            create_date=datetime.datetime.now(pytz.utc),
            description=vol.display_description,
            user=user,
            type=ty_pe,
            metering_group=mg.objects.get(id=metering_group_id),
        )
        LOG.info("User %s extended volume name: %s." % (user.username, vol.display_name))
        return HttpResponseRedirect("/feature/volume/")

# 删除磁盘
def delete(request, vol_id, dc):
    user = request.user
    if request.is_ajax():
        del_list = request.POST.get("vol_Json")
        json_list = json.loads(del_list)
        for x in json_list:
            dc = x.keys()[0]
            udc = set_dc(dc)
            cinder = cinder_token(user, udc)
            vol_ids = x.get(dc)
            for vol_id in vol_ids:
                vol = cinder.volumes.get(vol_id)
                status = vol.status
                if(status=="in-use"):
                    mess = "已经挂载的磁盘不能进行删除！"
                    return HttpResponse("4")
                cinder.volumes.delete(vol_id)
                LOG.info("User %s deleted volume name: %s." % (user.username, vol.display_name))
                volume_model.objects.filter(volume_id=vol_id).update(
                    # deleted_date =time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
                    deleted_date=datetime.datetime.now(pytz.utc)
                )
        return HttpResponse("1")
    else:
        udc = set_dc(dc)
        cinder = cinder_token(user, udc)
        try:
            v = cinder.volumes.get(vol_id)
            if(v.status=="deleting"):
                raise Exception
        except Exception:
            mess = "磁盘删除错误或已删除，如有错误请联系管理员！"
            return render_to_response('base.html',{"error_message":mess,"current_user": user})
        status = v.status
        if(status=="in-use"):
            mess = "已经挂载的磁盘不能进行删除！"
            return render_to_response('base.html',{"error_message":mess})
        cinder.volumes.delete(vol_id)
        volume_name = cinder.volumes.find(id=vol_id).display_name
        LOG.info("User %s deleted volume name: %s." % (user.username, volume_name))
        # 删除成功之后，需要在本地数据库磁盘表中加入删除时间。
        volume_model.objects.filter(volume_id=vol_id).update(
            # deleted_date =time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
            deleted_date=datetime.datetime.now(pytz.utc)
        )
    return HttpResponseRedirect("/feature/volume/")

def ajax_process(request, vol_name, dc):
    user = request.user
    udc = set_dc(dc)
    cinder = cinder_token(user, udc)
    try:
        vol_status = cinder.volumes.find(display_name=vol_name).status
    except:
        vol_status = "deleted"
    print vol_status
    return HttpResponse(vol_status)
