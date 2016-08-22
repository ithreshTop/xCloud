# coding=utf-8
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from feature import util
from django.contrib.auth.decorators import login_required


@login_required
def overview(request):
    user = request.user
    if user.username == 'admin':
        return HttpResponseRedirect("/logout/")
    types = ["experiment"]
    quotas = {}
    already_use = {}

    for t in types:
        quotas[t] = []
        already_use[t] = []
        udc = util.set_dc(t)
        nova = util.nova_token(user, udc)

        admin = util.nova_admin_token(udc)
        keystone = util.keystone_token(user, udc)
        quota = admin.quotas.get(keystone.tenant_id)
        cinder_admin = util.cinder_admin_token(udc)
        cinder = util.cinder_token(user, udc)
        cpu = 0
        ram = 0
        volume_size = 0
        servers = nova.servers.list()
        volumes = cinder.volumes.list()
        if len(servers):
            for server in servers:
                flavor = nova.flavors.get(server.flavor.get('id'))
                cpu += flavor.vcpus
                ram += flavor.ram
        if len(volumes):
            for volume in volumes:
                volume_size += cinder.volumes.get(volume.id).size
        quotas[t].append(quota.instances)
        quotas[t].append(quota.cores)
        quotas[t].append(quota.ram)
        quotas[t].append(cinder_admin.quotas.get(keystone.tenant_id).gigabytes)
        quotas[t].append(quota.floating_ips)

        already_use[t].append(len(servers))
        already_use[t].append(cpu)
        already_use[t].append(ram)
        already_use[t].append(volume_size)
        already_use[t].append(len(nova.floating_ips.list()))
    return render_to_response('pages/overview/overview.html', {"p_quotas": quotas["experiment"],
                                                               # "t_quotas": quotas["test"],
                                                               "p_already_use": already_use["experiment"],
                                                               # "t_already_use": already_use["test"],
                                                               "current_user": user
                                                               }
                              )