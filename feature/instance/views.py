__author__ = 'songjunting'
# coding:utf-8
from django.shortcuts import render_to_response,HttpResponse
from django.http import HttpResponseRedirect
import time, datetime, pytz
from feature import util
from django.contrib.auth.decorators import login_required
from feature.celerytask.tasks import bindingIP, networkCreate, bindingDefaultVolume, freeIP
from django.http import JsonResponse
from feature.instance.models import Instance
from feature.volume.models import VolumeToServer
from feature.serverlist.models import MetringGroup
import json
import logging
LOG = logging.getLogger("feature")
BUG = logging.getLogger("request")


@login_required
# 查询云主机
def instance(request):
    types = ["experiment"]
    user = request.user
    if user.username == 'admin':
        return HttpResponseRedirect("/logout/")
    novas = []
    cinders = []
    for t in types:
        udc = util.set_dc(t)
        nova = util.nova_token(user, udc)
        if request.is_ajax():
            servername = request.POST.get("servername", None)
            status = 0
            if servername is not None:
                try:
                    nova.servers.find(name=servername)
                    status = 1
                except:
                    status = 0
            return HttpResponse(status)
        n = {}
        c = {}
        n[t] = {}
        c[t] = {}
        cinder = util.cinder_token(user, udc)
        n[t]["server"] = nova.servers.list()
        n[t]["image"] = nova.images.list()
        n[t]["flavor"] = nova.flavors.list()
        c[t]["volume"] = cinder.volumes.list()
        novas.append(n)
        cinders.append(c)

    return render_to_response("pages/instance/instance.html",
                              {"novas": novas,
                               "cinders": cinders,
                               "current_user": user})


def createForm(request):
    udc = util.set_dc()
    user = request.user
    if user.username == 'admin':
        return HttpResponseRedirect("/logout/")
    nova = util.nova_token(user, udc)
    type_list = nova.flavors.list()
    image_list = nova.images.list()
    try:
        import operator
    except ImportError:
        cmpfun = lambda x: x.ram
        imgfun = lambda x: x.name
    else:
        cmpfun = operator.attrgetter("ram")
        imgfun = operator.attrgetter("name")
    type_list.sort(key=cmpfun, reverse=False)
    image_list.sort(key=imgfun, reverse=False)    
    return render_to_response("pages/instance/create_forms.html",
                              {"instance_detail": nova.servers.list(),
                               "flavor_detail": type_list,
                               "image_detail": image_list,
                               "metering_group": MetringGroup.objects.all(),
                               "current_user": user})


# 计算配额
def calculate_quotas(request):
    user = request.user
    types = ["experiment"]
    quotas = {}
    already_use = {}

    for t in types:
        quotas[t] = {}
        already_use[t] = {}
        udc = util.set_dc(t)
        nova = util.nova_token(user, udc)

        admin = util.nova_admin_token(udc)
        keystone = util.keystone_token(user, udc)
        quota = admin.quotas.get(keystone.tenant_id)
        cpu = 0
        ram = 0
        insNum = len(nova.servers.list())
        if nova.servers.list():
            for server in nova.servers.list():
                cpu += nova.flavors.get(server.flavor.get('id')).vcpus
                ram += nova.flavors.get(server.flavor.get('id')).ram

        quotas[t]["cpu"] = quota.cores
        quotas[t]["ram"] = quota.ram
        quotas[t]["insNum"] = quota.instances

        already_use[t]["cpu"] = cpu
        already_use[t]["ram"] = ram
        already_use[t]["insNum"] = insNum

    return quotas, already_use


# 创建云主机
def instanceCreate(request):
    insInfo = request.POST['listInsJson']
    insInfoJson = json.loads(insInfo)
    
    user = request.user
    q = calculate_quotas(request)

    for ins in insInfoJson:
        ty_pe = ins["htype"]
        udc = util.set_dc(ty_pe)
        nova = util.nova_token(user, udc)
        neutron = util.neutron_token(udc)
        external = [e for e in neutron.list_networks()['networks'] if e['router:external'] is True][0]['name']

        if len(nova.networks.list()) < 2:
            networkCreate.delay(user, udc)

        hostname0 = ins["hname"]
        flavor_ram = int(ins["hflavor"].split("|")[1][0:-2])
        flavor_cpu = int(ins["hflavor"].split("|")[0][0])
        flavor = nova.flavors.find(ram=flavor_ram, vcpus=flavor_cpu)
        image = nova.images.find(name=ins["himage"])
        use = ins["hdescribe"]
        volume_size = ins["vsize"]
        number = int(ins["hnumber"])
        group_name = ins["group"]
        for x in range(number):
            if x >= 1:
                hostname = hostname0 + "_" + str(x)
            else:
                hostname = hostname0
            q[1][ty_pe]["cpu"] += flavor.vcpus
            q[1][ty_pe]["ram"] += flavor.ram
            q[1][ty_pe]["insNum"] += 1

            if q[1][ty_pe]["cpu"] <= q[0][ty_pe]["cpu"] and q[1][ty_pe]["ram"] <= q[0][ty_pe]["ram"] \
                    and q[1][ty_pe]["insNum"] <= q[0][ty_pe]["insNum"]:
                i = nova.servers.create(name=hostname, image=image, flavor=flavor)
                group = MetringGroup.objects.get(group_name=group_name)
                LOG.info("User %s create instance name:%s" % (user.username, hostname))
                deadline = datetime.datetime.now(pytz.utc) + datetime.timedelta(days=30)
                Instance.objects.create(name=hostname, tenant_name_id=user.id, flavor=ins["hflavor"],
                                        image=ins["himage"], network=user.username, metering_group=group,
                                        describe=use, create_time=datetime.datetime.now(pytz.utc), deadline=deadline,
                                        type=ty_pe, instance_id=i.id)
                bindingIP.delay(user=user, external=external, instanceId=i.id, udc=udc)
                if volume_size != '0':
                    bindingDefaultVolume.delay(user=user, volume_size=volume_size, hostname=hostname,
                                               instanceId=i.id, udc=udc, ty_pe=ty_pe, group=group)
            else:
                return HttpResponse("2")
    return HttpResponse("1")


# 绑定云硬盘
def attachVolume(request):
    vol_id = request.POST.get("volume").split(",")[1]
    host_id = request.POST.get("ins_id")
    dc = request.POST.get("volume").split(",")[0]
    udc = util.set_dc(dc)
    user = request.user
    nova = util.nova_token(user, udc)
    cinder = util.cinder_token(user, udc)

    cinder.volumes.attach(vol_id, host_id, mountpoint='/dev/vdc', mode='rw')
    VolumeToServer.objects.create(server_id=host_id, volume_id=vol_id)
    LOG.info("User %s attached instance :%s to volume :%s" % (user.username,
                                                              nova.servers.get(host_id).name,
                                                              cinder.volumes.get(vol_id).display_name))
    return HttpResponseRedirect("/feature/instance/")


# 重启云主机
def rebootInstance(request, host_id, dc):
    udc = util.set_dc(dc)
    user = request.user
    nova = util.nova_token(user, udc)
    ins = nova.servers.get(host_id)
    try:
        nova.servers.reboot(ins)
        LOG.info("User %s rebooted instance :%s" % (user.username, ins.name))
        return HttpResponseRedirect("/feature/instance/")
    except:
        return render_to_response("base.html", {"error_message": "当前状态不可重启！"})


# 关闭云主机
def stopInstance(request, host_id, dc):
    udc = util.set_dc(dc)
    user = request.user
    nova = util.nova_token(user, udc)
    ins = nova.servers.get(host_id)
    try:
        nova.servers.stop(ins)
        LOG.info("User %s stopped instance :%s" % (user.username, ins.name))
        while nova.servers.get(host_id).status == "ACTIVE":
            time.sleep(2)
        return HttpResponseRedirect("/feature/instance/")
    except:
        return render_to_response("base.html", {"error_message": "当前状态不可关机！"})


# 打开云主机
def startInstance(request, host_id, dc):
    udc = util.set_dc(dc)
    user = request.user
    nova = util.nova_token(user, udc)

    ins = nova.servers.get(host_id)
    try:
        nova.servers.start(ins)
        LOG.info("User %s started instance :%s" % (user.username, ins.name))
        while not nova.servers.get(host_id).status == "ACTIVE":
            time.sleep(2)
        return HttpResponseRedirect("/feature/instance/")
    except:
        return render_to_response("base.html", {"error_message": "当前状态不可开机！"})


# 删除云主机
def deleteInstance(request, host_id, dc):
    user = request.user

    if request.is_ajax():
        LOG.info("User %s deleted some instances:")
        delInsInfo = request.POST['listHostJson']
        delInsInfoJson = json.loads(delInsInfo)

        for h in delInsInfoJson:
            ty_pe = h.keys()[0]
            udc = util.set_dc(ty_pe)
            nova = util.nova_token(user, udc)
            cinder = util.cinder_token(user, udc)
            length = len(nova.servers.list())
            ins_ids = h.get(ty_pe)
            volumes = []
            for vol in cinder.volumes.list():
                if vol.attachments:
                    volumes.append(vol)
            if ins_ids:
                for ins_id in ins_ids:
                    ins = nova.servers.get(ins_id)
                    for v in volumes:
                        if v.attachments[0]["server_id"] == ins_id:
                            cinder.volumes.detach(v.attachments[0]["volume_id"])
                            break
                    nova.servers.delete(ins)
                    LOG.info("User %s deleted instance :%s" % (user.username, ins.name))
                    Instance.objects.filter(instance_id=ins_id).update(
                        delete_time=datetime.datetime.now(pytz.utc))
            while len(nova.servers.list()) > (length - len(ins_ids)):
                time.sleep(1)
            freeIP.delay(user, udc)
        return HttpResponse(1)
    else:
        udc = util.set_dc(dc)
        nova = util.nova_token(user, udc)
        length = len(nova.servers.list())
        ins = nova.servers.get(host_id)

        cinder = util.cinder_token(user, udc)
        for vol in cinder.volumes.list():
            if vol.attachments:
                if vol.attachments[0]["server_id"] == host_id:
                    cinder.volumes.detach(vol.attachments[0]["volume_id"])
                    break

        nova.servers.delete(ins)
        LOG.info("User %s deleted instance :%s" % (user.username, ins.name))
        Instance.objects.filter(instance_id=host_id).update(
            delete_time=datetime.datetime.now(pytz.utc))
        while len(nova.servers.list()) == length:
            time.sleep(1)
        freeIP.delay(user, udc)
    return HttpResponseRedirect("/feature/instance/")


# 打开控制台
def startConsole(request, host_id, dc):
    udc = util.set_dc(dc)
    user = request.user
    nova = util.nova_token(user, udc)
    instance1 = nova.servers.get(host_id)
    image_id = instance1.image["id"]
    image = nova.images.get(image_id)
    if instance1.status == 'ACTIVE':
        console = instance1.get_vnc_console('novnc')
        return render_to_response("pages/instance/vnc_console.html",
                                  {"console_url": console["console"]["url"],
                                   "current_user": user,
                                   "image": image})
    else:
        return render_to_response("base.html", {"error_message": u"当前主机状态不能打开控制台，请确认主机状态是否为ACTIVE"})



# 修改主机名
def renameInstance(request):
    dc = request.POST.get("ins_type")
    udc = util.set_dc(dc)
    user = request.user
    nova = util.nova_token(user, udc)
    hostname = request.POST.get("hostname1")
    host_id = request.POST.get("host_id")
    host = nova.servers.get(host_id)
    hostname_old = host.name
    if hostname_old == hostname:
        return HttpResponseRedirect("/feature/instance/")
    host.update(name=hostname)
    LOG.info("User %s renamed instance to :%s" % (user.username, hostname))
    Instance.objects.filter(instance_id=host_id).update(name=hostname)
    return HttpResponseRedirect("/feature/instance/")


# 展示主机详细信息
def show_instance_detail(request, host_id, dc):
    udc = util.set_dc(dc)
    user = request.user
    nova = util.nova_token(user, udc)
    cinder = util.cinder_token(user, udc)
    ins = nova.servers.get(host_id)
    ins_d = Instance.objects.get(instance_id=host_id)
    cin = []
    for c in cinder.volumes.list():
        if c.status == "in-use" and c.attachments[0]["server_id"] == host_id:
            cin.append(c)

    return render_to_response("pages/instance/instance_detail.html", {"ins": ins, "ins_d": ins_d,
                                                                      "cin": cin, "flavor": nova.flavors.list(),
                                                                      "image": nova.images.list(),
                                                                      "current_user": user})

# ajax过程
def ajax_process(request, host_id, dc):
    udc = util.set_dc(dc)
    user = request.user
    nova = util.nova_token(user, udc)
    ins = nova.servers.get(host_id)
    try:
        response_data = {'ins_network': ins.networks[user.username][1], 'ins_status': ins.status}
    except:
        response_data = {'ins_network': "", 'ins_status': "BUILD"}
    return JsonResponse(response_data)
