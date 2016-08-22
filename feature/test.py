#!/usr/bin/env python
#coding:utf-8
__author__ = 'sunyaxiong'

from django.shortcuts import render_to_response

def base(request):
    return render_to_response('base.html')