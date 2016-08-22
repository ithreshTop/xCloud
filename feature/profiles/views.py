#!/usr/bin/env python
# coding:utf-8
__author__ = 'sunyaxiong'

from django.shortcuts import render_to_response
from keystoneclient.v2_0 import client as ksclient
from django.contrib.auth.decorators import login_required


@login_required
def changePassword(request):
    if request.method == 'POST':

        userName = request.user
        newPassword = request.POST.get('new_password')
        print userName
        keystone = ksclient.Client(auth_url="http://10.1.201.20:35357/v2.0",
                                            username="admin",
                                            password="admin",
                                            tenant_name="admin")
        keystone.users.update_password(userName, newPassword)
        return render_to_response("login.html")