# coding=utf-8

from django.shortcuts import render_to_response

# 用于页面跳转
def jump(request, code):
    if code == "2":
        message = "云主机配置超出配额，请查看概览页面配额限制！"
    elif code == "4":
        message = "已经挂载的磁盘不能进行删除！"
    else:
        message = "未知错误发生！"
    return render_to_response("base.html",
                              {"error_message": message})
