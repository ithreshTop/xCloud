# coding=utf-8

from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from feature import util

@login_required
def image(request):

    user = request.user
    udc = util.set_dc()
    nova = util.nova_token(user, udc)
    print nova.images.list
    return render_to_response("pages/image/image.html",
                              {"image_status": nova.images.list(),
                               "current_user": user})
