#coding:utf-8
from keystoneclient.v2_0 import client as keystone_client
from novaclient import client as nova_client
from cinderclient import client as cinder_client
from account.models import UserProfile
from neutronclient.v2_0 import client as neutron_client          # test
from ceilometerclient.v2 import client as ceilometer_client
from django.conf import settings


def set_dc(dc=None):
    if dc == 'test':
        udc = settings.DATA_CENTER_TEST
    else:
        udc = settings.DATA_CENTER_PRO
    return udc
    

def keystone_token(user, udc):
    keystone_password = UserProfile.objects.filter(user_id__exact=user.id)[0].keystone_password
    keystone = keystone_client.Client(username=user.username,
                                      password=keystone_password,
                                      tenant_name=user.username,
                                      auth_url=udc["auth_url"])
    return keystone

# test
def keystone_admin_token(udc):
    keystone = keystone_client.Client(username=udc["username"],
                                      password=udc["password"],
                                      tenant_name=udc["tenant_name"],
                                      auth_url=udc["auth_url"])
    return keystone

def nova_token(user, udc):
    keystone_password = UserProfile.objects.filter(user_id__exact=user.id)[0].keystone_password
    nova = nova_client.Client('2', user.username, keystone_password, user.username, udc["auth_url"])
    return nova

def nova_admin_token(udc):
    adminnova = nova_client.Client('2', udc["username"], udc["password"], udc["tenant_name"], udc["auth_url"])
    return adminnova

def cinder_token(user, udc):
    keystone_password = UserProfile.objects.filter(user_id__exact=user.id)[0].keystone_password
    cinder = cinder_client.Client('1', user.username, keystone_password, user.username, udc["auth_url"])
    return cinder

def cinder_admin_token(udc):
    admincinder = cinder_client.Client('1', udc["username"], udc["password"], udc["tenant_name"], udc["auth_url"])
    return admincinder

def neutron_token(udc):
    neutron = neutron_client.Client(username=udc["username"],
                                    password=udc["password"],
                                    tenant_name=udc["tenant_name"],
                                    auth_url=udc["auth_url"])
    return neutron

def neutron_user_token(user, udc):
    keystone_password = UserProfile.objects.filter(user_id__exact=user.id)[0].keystone_password
    neutron = neutron_client.Client(username=user.username,
                                    password=keystone_password,
                                    tenant_name=user.username,
                                    auth_url=udc["auth_url"])
    return neutron

def ceilometer_admin_token(udc):
    adminceilometer = ceilometer_client.Client('2', udc["username"], udc["password"], udc["tenant_name"], udc["auth_url"])
    return adminceilometer
