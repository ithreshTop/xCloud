# coding:utf8
from models import Server
from django.shortcuts import render_to_response

ListDetail = []
def listDetail(request):
    user = request.user
    for list_server in Server.objects.filter(tenant_name_id=user.id):
        ListDetail.append(list_server)
    return render_to_response("pages/serverlist/serverlist_price_detail.html", {"serverinfo": ListDetail,
                                                                                     "current_user": user,
                                                                                    })
