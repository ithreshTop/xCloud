#!/usr/bin/env python
# coding:utf-8

from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.core.mail import send_mail

@login_required
def mail(request):
    user = request.user

    if request.method == 'POST':
        email = user.email
        sub = request.POST.get("subject")
        cate = request.POST.get("category")
        if cate==1:
            cate_string ="资源申请"
        elif cate==2:
            cate_string="问题反馈"
        else:
            cate_string="投诉建议"
        sub_text = "from " + user.username +",about: "+cate_string+ " : "+ sub
        context = request.POST.get("context")
        send_mail(sub_text,context,email,["eCloud@enn.cn",],
                  fail_silently=True)
        return HttpResponseRedirect('/feature/mail/')

    return render_to_response("pages/mail/mail.html",{'current_user': user})