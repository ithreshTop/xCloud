# coding: utf-8
import random
from django.shortcuts import render_to_response, render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.template import RequestContext
from django.contrib import auth

from account.forms import UserForm, ChangepwdForm
from account.models import UserProfile
from feature.celerytask.tasks import user_create
from feature.util import set_dc, keystone_token
import logging
LOG = logging.getLogger('feature')
BUG = logging.getLogger('request')
# Create your views here.


def Login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        print form
        if form.is_valid:
            user = form.get_user()
            if user:
                if not UserProfile.objects.filter(user_id=user.id):
                    keystone_password = "1qazxsw@%s" % random.randrange(100000, 999999)
                    UserProfile.objects.create(
                            user=user,
                            mobile=None,
                            keystone_password=keystone_password)
                    udc = set_dc()
                    user_create(user=user, keystone_pwd=keystone_password, udc=udc)
                    #udc = set_dc('test')
                    #user_create(user=user, keystone_pwd=keystone_password, udc=udc)
                else:
                    try:
                        udc = set_dc()
                        keystone_token(user, udc)
                    except:
                        ksuser = UserProfile.objects.get(user_id=user.id)
                        udc = set_dc()
                        user_create(user=user, keystone_pwd=ksuser.keystone_password, udc=udc)
                if user.is_active:
                    login(request, user)
                    LOG.info("User %s login in"%(user.username))
                else:
                    return render_to_response('login.html', {'info': '该用户处于挂起状态,'})
                return HttpResponseRedirect('/feature/overview/')
        return render_to_response('login.html', {'info': '用户名或密码错误', 'form': form})
    return render_to_response('login.html')



def regist(request):
    if request.method == 'POST':
        user = User()
        form = UserForm(data=request.POST, instance=user)
        if form.is_valid():
            keystone_password = "1qazxsw@%s" % random.randrange(100000, 999999)
            form.save(keystone_password)
            udc = set_dc()
            user_create(user=user, keystone_pwd=keystone_password, udc=udc)
            #udc = set_dc('test')
            #user_create(user=user, keystone_pwd=keystone_password, udc=udc)
            return HttpResponseRedirect('/accounts/login/', {'info': 'regist success'})

        return render_to_response('regist.html', {"form": form})

    return render_to_response('regist.html', {"form": UserForm})


def Logout(request):
    logout(request)
    return HttpResponseRedirect('/accounts/login/')


def changepwd(request):
    if request.method == 'GET':
        form = ChangepwdForm()
        return render_to_response('changepwd.html', RequestContext(request, {'form': form,}))
    else:
        form = ChangepwdForm(request.POST)
        if form.is_valid():
            username = request.user.username
            oldpassword = request.POST.get('oldpassword', '')
            user = auth.authenticate(username=username, password=oldpassword)
            if user is not None and user.is_active:
                newpassword = request.POST.get('newpassword1', '')
                user.set_password(newpassword)
                user.save()
                return render_to_response('index.html', RequestContext(request,{'changepwd_success':True}))
            else:
                return render_to_response('changepwd.html', RequestContext(request, {'form': form,'oldpassword_is_wrong':True}))
        else:
            return render_to_response('changepwd.html', RequestContext(request, {'form': form,}))


def ajax_process(request):
    status = 0
    if request.is_ajax():
        username = request.POST.get("username", None)
        email = request.POST.get("email", None)
        mobile = request.POST.get("mobile", None)
        if username is not None:
            user = User.objects.filter(username__exact=username)
            if user:
                status = 1
        if email is not None:
            user = User.objects.filter(email__exact=email)
            if user:
                status = 1
        if mobile is not None:
            user = UserProfile.objects.filter(mobile__exact=mobile)
            if user:
                status = 1
    return HttpResponse(status)


def not_found(request):
    user = request.user
    return render(request, '404.html', {"current_user": user})


def server_error(request):
    user = request.user
    return render(request, '500.html', {"current_user": user})