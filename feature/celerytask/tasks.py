#coding:utf-8

from __future__ import absolute_import
from celery import shared_task
from django.shortcuts import render_to_response
from feature.util import keystone_admin_token, neutron_user_token, neutron_token, \
     cinder_token,nova_token, cinder_admin_token, keystone_token
from feature.instance.models import Instance
from feature.volume.models import VolumeToServer, Volume
from django.core.mail import send_mail
import time
import datetime, pytz
from feature.ldap_search import ldap_user_search


def user_create(user, keystone_pwd, udc):
    keystone_admin = keystone_admin_token(udc)
    keystone_admin.tenants.create(tenant_name=user.username, description="", enabled=True)
    tenants = keystone_admin.tenants.list()
    my_tenant = [x for x in tenants if x.name == user.username][0]
    keystone_admin.users.create(name=user.username,
                                password=keystone_pwd,
                                email=user.email,
                                tenant_id=my_tenant.id)
    add_security_group.delay(user, udc)

    nova = nova_token(user, udc)
    if len(nova.networks.list()) < 2:
        networkCreate.delay(user, udc)


@shared_task
def add_security_group(user,udc):
    # 添加安全组规则
    neutron = neutron_user_token(user, udc)
    security_group_id = neutron.list_security_groups()['security_groups'][0]['id']
    protocol = ['ICMP', 'TCP', 'UDP']
    direction = ['egress', 'ingress']
    for p in protocol:
        for d in direction:
            neutron.create_security_group_rule(
                {'security_group_rule':
                     {'security_group_id': security_group_id,
                      'protocol': p,
                      'direction': d
                      }})


@shared_task
# 绑定浮动IP
def bindingIP(user, external, instanceId, udc):
    nova = nova_token(user, udc)

    while nova.servers.get(instanceId).status == "BUILD":
        time.sleep(1)
    """flag = 0
    if len(nova.floating_ips.list()) > 0:
        for float_ip in nova.floating_ips.list():
            if float_ip.fixed_ip is None:
                nova.servers.get(instanceId).add_floating_ip(float_ip)
                Instance.objects.filter(name=nova.servers.get(instanceId).name).update(public_ip=float_ip.ip)
                flag = 1
                break
    if flag == 0:"""
    float_ip = nova.floating_ips.create(pool=external)
    nova.servers.get(instanceId).add_floating_ip(float_ip)
    Instance.objects.filter(instance_id=instanceId).update(public_ip=float_ip.ip)


@shared_task
# 创建网络 test
def networkCreate(user, udc):
    neutron = neutron_token(udc)
    neutron_user = neutron_user_token(user, udc)
    keystone = keystone_admin_token(udc)
    tenant = None
    segmentation_id = 0

    for t in keystone.tenants.list():
        if t.name == user.username:
            tenant = t
            break
    for s_i in range(463, 500):
        flag = 0
        for n in neutron.list_networks()['networks']:
            if n['provider:segmentation_id'] == s_i:
                flag = 1
                continue
        if flag == 0:
            segmentation_id = s_i
            break

    network = neutron.create_network({'network': {'name':  user.username,
                                                  'tenant_id': tenant.id,
                                                  'provider:network_type': 'vlan',
                                                  'provider:physical_network': 'physnet2',
                                                  'provider:segmentation_id': segmentation_id}})

    subnet = neutron.create_subnet({'subnet': {'name': user.username,
                                               'network_id': network['network']['id'],
                                               'ip_version': 4,
                                               "dns_nameservers": [],
                                               "enable_dhcp": True,
                                               "cidr": '192.168.1.0/24',
                                               "gateway_ip": "192.168.1.1",
                                               'tenant_id': tenant.id}})

    external = [e for e in neutron.list_networks()['networks'] if e['router:external'] is True][0]['id']
    router = neutron.create_router({'router': {'name': user.username,
                                               'external_gateway_info': {"network_id": external,
                                                                         "enable_snat": True},
                                               'tenant_id': tenant.id}})

    neutron_user.add_interface_router(router['router']['id'], {'subnet_id': subnet['subnet']['id'],
                                                               })


@shared_task
# 绑定默认云盘
def bindingDefaultVolume(user, volume_size, hostname, instanceId, udc, ty_pe, group):
    nova = nova_token(user, udc)
    cinder = cinder_token(user, udc)
    cinder_admin = cinder_admin_token(udc)
    keystone = keystone_token(user, udc)
    total_size = 0

    for c in cinder.volumes.list():
        total_size += c.size

    total_size += int(volume_size)
    if total_size <= cinder_admin.quotas.get(keystone.tenant_id).gigabytes:
        cin = cinder.volumes.create(display_name=hostname, size=volume_size, display_description="主机扩展磁盘")
        Volume.objects.create(name=hostname, volume_id=cin.id, size=volume_size,
                              create_date=datetime.datetime.now(pytz.utc), description="主机扩展磁盘",
                              type=ty_pe, user=user, metering_group=group)
        while nova.servers.get(instanceId).status == "BUILD" or \
                        cinder.volumes.get(cin.id).status == "creating":
            time.sleep(1)
        cinder.volumes.attach(cin.id, instanceId, mountpoint='/dev/vdc', mode='rw')
        VolumeToServer.objects.create(server_id=instanceId, volume_id=cin.id)
    else:
        return render_to_response("base.html", {"error_message": "云主机配置超出配额，请查看概览页面配额限制！"})
          

@shared_task
# 释放多余IP
def freeIP(user, udc):
    nova = nova_token(user, udc)
    for spare_ip in nova.floating_ips.list():
        if spare_ip.fixed_ip is None:
            nova.floating_ips.delete(spare_ip)

@shared_task
# 到期提醒
def is_deadline():
    instances = Instance.objects.filter(delete_time=None)
    for ins in instances:
        if (ins.deadline - datetime.datetime.now(pytz.utc)).days == 7:
            context = u'您的主机' + ins.name +\
                      u'使用时间即将到期，如需延长使用，请回复邮件申请！'
            email = [ins.tenant_name.email]
            send_mail(u'云主机到期通知', context, 'eCloud@enn.cn', email,
                      fail_silently=True)

@shared_task
# 定期同步ldap信息
def ldap_update():
    ldap_user_search()