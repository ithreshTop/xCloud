from django.shortcuts import render_to_response

__author__ = 'temple'
import json

from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse  # noqa
from django.utils.translation import ugettext_lazy as _
from django.views.generic import View  # noqa
from feature.util import nova_token, cinder_token, keystone_token, cinder_admin_token, set_dc,neutron_token, \
    neutron_user_token


class JSONView(View):

    @property
    def is_router_enabled(self):
        network_config = getattr(settings, 'OPENSTACK_NEUTRON_NETWORK', {})
        return network_config.get('enable_router', True)

    def add_resource_url(self, view, resources):
        user = self.request.user
        udc = set_dc("experiment")
        keystone = keystone_token(user,udc)
        tenant_id = keystone.auth_tenant_id
        for resource in resources:
            if (resource.get('tenant_id')
                    and tenant_id != resource.get('tenant_id')):
                continue
            resource['url'] = reverse(view, None, [str(resource['id'])])

    def _check_router_external_port(self, ports, router_id, network_id):
        for port in ports:
            if (port['network_id'] == network_id
                    and port['device_id'] == router_id):
                return True
        return False

    def _get_servers(self, request):
        # Get nova data
        user = request.user
        udc = set_dc("experiment")
        nova = nova_token(user,udc)
        try:
            servers = nova.servers.list()
        except Exception:
            servers = []
        data = []
        console_type = getattr(settings, 'CONSOLE_TYPE', 'AUTO')
        # lowercase of the keys will be used at the end of the console URL.
        for server in servers:
            server_data = {'name': server.name,
                           'status': server.status,
                           'task': getattr(server, 'OS-EXT-STS:task_state'),
                           'id': server.id,
                           'networks':server.networks,
                           }
            data.append(server_data)
       # self.add_resource_url('feature:project:instances:detail', data)
        return data

    def _get_networks(self, request):
        # Get neutron data
        # if we didn't specify tenant_id, all networks shown as admin user.
        # so it is need to specify the networks. However there is no need to
        # specify tenant_id for subnet. The subnet which belongs to the public
        # network is needed to draw subnet information on public network.
        user = request.user
        udc = set_dc("experiment")
        neutron = neutron_user_token(user,udc)
        try:
            neutron_networks = neutron.list_networks()['networks']
        except Exception:
            neutron_networks = []
        networks = [{'name': network['name'],
                     'id': network['id'],
                    # 'subnets': [{'cidr': subnet['cidr']}
                    #             for subnet in network['subnets']],
                     'router:external': network['router:external']}
                    for network in neutron_networks]


        # Add public networks to the networks list
        if self.is_router_enabled:
            try:
                neutron_public_networks = neutron.list_networks(
                    **{'router:external': True})
            except Exception:
                neutron_public_networks = []
            my_network_ids = [net['id'] for net in networks]
            for publicnet in neutron_public_networks["networks"]:
                if publicnet['id'] in my_network_ids:
                    continue

                networks.append({
                    'name': publicnet['name'],
                    'id': publicnet['id'],
                   # 'subnets': subnets,
                    'router:external': publicnet['router:external']})

        return sorted(networks,
                      key=lambda x: x.get('router:external'),
                      reverse=True)

    def _get_routers(self, request):
        user = request.user
        udc = set_dc("experiment")
        neutron = neutron_user_token(user,udc)
        if not self.is_router_enabled:
            return []
        try:
            neutron_routers = neutron.list_routers()["routers"]
        except Exception:
            neutron_routers = []

        routers = [{'id': router['id'],
                    'name': router['name'],
                    'status': router['status'],
                    'external_gateway_info': router['external_gateway_info']}
                   for router in neutron_routers]
        return routers

    def _get_ports(self, request):
        user = request.user
        udc = set_dc("experiment")
        neutron = neutron_user_token(user,udc)
        try:
            neutron_ports = neutron.list_ports()["ports"]
        except Exception:
            neutron_ports = []

        ports = [{'id': port['id'],
                  'network_id': port['network_id'],
                  'device_id': port['device_id'],
                  'fixed_ips': port['fixed_ips'],
                  'device_owner': port['device_owner'],
                  'status': port['status']}
                 for port in neutron_ports
                 if port['device_owner'] != 'network:router_ha_interface']
        return ports

    def _prepare_gateway_ports(self, routers, ports):
        # user can't see port on external network. so we are
        # adding fake port based on router information
        for router in routers:
            external_gateway_info = router.get('external_gateway_info')
            if not external_gateway_info:
                continue
            external_network = external_gateway_info.get(
                'network_id')
            if not external_network:
                continue
            if self._check_router_external_port(ports,
                                                router['id'],
                                                external_network):
                continue
            fake_port = {'id': 'gateway%s' % external_network,
                         'network_id': external_network,
                         'device_id': router['id'],
                         'fixed_ips': []}
            ports.append(fake_port)

    def get(self, request, *args, **kwargs):
        #data = {}
        #self._prepare_gateway_ports(data['routers'], data['ports'])
        #json_string = json.dumps(data, ensure_ascii=False)
        user = request.user
        return render_to_response("topo.html",{
                "current_user": user,
                'servers': self._get_servers(request),
                'networks': self._get_networks(request),
                'ports': self._get_ports(request),
                'routers': self._get_routers(request)})
