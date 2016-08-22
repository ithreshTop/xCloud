# coding=utf-8

from django.shortcuts import render_to_response
from feature.instance import models as insdb
from feature.volume import models as voldb
from feature.serverlist import models as solarwindsdb
import datetime, pytz
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect


Price = {
    "cpu": "50",        # 50/C/月
    "ram": "30",        # 30/G/月
    "volume": "0.4",    # 0.4/G/月
    "instance": "120"   # 每个固定增加主机价格/月
}



@login_required()
def metering(request):
    user = request.user
    if user.username == 'admin':
        return HttpResponseRedirect("/logout/")
    month_begin = datetime.datetime.now(pytz.utc).replace(day=1, hour=0, minute=0, second=0)
    month_end = datetime.datetime.now(pytz.utc)
    if request.method == "POST":
        year = int(request.POST.get("year"))
        month = int(request.POST.get("month"))
        month_begin = datetime.datetime(year=year, month=month, day=1,
                                        hour=0, minute=0, second=0, tzinfo=pytz.utc)
        if month == datetime.datetime.now().month and year == datetime.datetime.now().year:
            month_end = datetime.datetime.now(pytz.utc)
        else:
            if month == 12:
                month_end = datetime.datetime(year=year+1, month=1, day=1,
                                              hour=0, minute=0, second=0, tzinfo=pytz.utc)-datetime.timedelta(days=1)
            else:
                month_end = datetime.datetime(year=year, month=month+1, day=1,
                                              hour=0, minute=0, second=0, tzinfo=pytz.utc)-datetime.timedelta(days=1)
    total_cpu = 0
    total_ram = 0.0
    total_vol = 0.0
    total_ins = 0
    cpu_total_price = 0.0
    ram_total_price = 0.0
    vol_total_price = 0.0
    ins_total_price = 0.0
    # 实例化solarwinds数据库资源计费数据
    solarwinds_total_disk, solarwinds_total_ram, solarwinds_total_cpu, solarwinds_total_swins,\
           solarwinds_cpu_total_price, solarwinds_ram_total_price, solarwinds_disk_total_price, \
                                                    swins_total_price = solarwinds_metering(request)
    # 获取租户CPU，内存使用量
    for ins in insdb.Instance.objects.filter(tenant_name_id=user.id):
        cpu = int(ins.flavor.split("|")[0][0])
        ram = float(ins.flavor.split("|")[1][0:-2])
        c_time = ins.create_time
        d_time = ins.delete_time
        if month_begin <= c_time < month_end:
            if d_time:
                if d_time >= month_end:
                    during_day = (month_end-c_time).days
                else:
                    during_day = (d_time - c_time).days
            else:
                during_day = (month_end - c_time).days
        elif c_time < month_begin:
            if d_time:
                if d_time >= month_end:
                    during_day = (month_end-month_begin).days
                elif d_time <= month_begin:
                    during_day = -1
                else:
                    during_day = (d_time - month_begin).days
            else:
                during_day = (month_end - month_begin).days
        else:
            during_day = -1

        if during_day != -1:
            cpu_price = float(Price["cpu"]) / 30 * during_day * cpu
            ram_price = float(Price["ram"]) / 30 / 1024 * during_day * ram
            ins_price = float(Price["instance"]) / 30 * during_day
            total_cpu += cpu
            total_ram += ram/1024
            total_ins += 1
            cpu_total_price += cpu_price
            ram_total_price += ram_price
            ins_total_price += ins_price

    # 获取租户磁盘使用量
    vol_list = voldb.Volume.objects.filter(user_id=user.id)
    for vol in vol_list:
        vol_size = vol.size
        c_time = vol.create_date
        d_time = vol.deleted_date
        if month_begin <= c_time < month_end:
            if d_time:
                if d_time >= month_end:
                    during_day = (month_end-c_time).days
                else:
                    during_day = (d_time - c_time).days
            else:
                during_day = (month_end - c_time).days
        elif c_time < month_begin:
            if d_time:
                if d_time >= month_end:
                    during_day = (month_end-month_begin).days
                elif d_time <= month_begin:
                    during_day = -1
                else:
                    during_day = (d_time - month_begin).days
            else:
                during_day = (month_end - month_begin).days
        else:
            during_day = -1

        if during_day != -1:
            vol_price = float(Price["volume"])/30 * vol_size * during_day
            total_vol += vol_size
            vol_total_price += vol_price
    return render_to_response("pages/metering/metering.html", {'current_user': user,
                                                               'ram': round(total_ram, 2),
                                                               'cpu': total_cpu,
                                                               'vol': total_vol,
                                                               "ins": total_ins,
                                                               "vol_total_price": round(vol_total_price, 2),
                                                               "cpu_total_price": round(cpu_total_price, 2),
                                                               "ram_total_price": round(ram_total_price, 2),
                                                               "price": Price,
                                                               "ins_total_price": round(ins_total_price, 2),
                                                               "solarwinds_cpu": solarwinds_total_cpu,
                                                               "solarwinds_disk": solarwinds_total_disk,
                                                               "solarwinds_ram": solarwinds_total_ram,
                                                               "solarwinds_swins": solarwinds_total_swins,
                                                               "solarwinds_ram_total_price": round(solarwinds_ram_total_price, 2),
                                                               "solarwinds_cpu_total_price": round(solarwinds_cpu_total_price, 2),
                                                               "solarwinds_disk_total_price": round(solarwinds_disk_total_price, 2),
                                                               "solarwinds_swins_total_price": round(swins_total_price, 2),
                                                               "month": month_begin,
                                                               })



# 主机价格计算明细
def instance_metering_detail(request, y, m):
    user = request.user
    year = int(y)
    month = int(m)
    month_begin = datetime.datetime(year=year, month=month, day=1, hour=0, minute=0, second=0, tzinfo=pytz.utc)
    if month == datetime.datetime.today().month and year == datetime.datetime.today().year:
        month_end = datetime.datetime.now(pytz.utc)
    else:
        if month == 12:
            month_end = datetime.datetime(year=year+1, month=1, day=1,
                                          hour=0, minute=0, second=0, tzinfo=pytz.utc)-datetime.timedelta(days=1)
        else:
            month_end = datetime.datetime(year=year, month=month+1, day=1,
                                          hour=0, minute=0, second=0, tzinfo=pytz.utc)-datetime.timedelta(days=1)

    host_list = []
    for i in insdb.Instance.objects.filter(tenant_name_id=user.id):
        host_price_detail = {}
        cpu = int(i.flavor.split("|")[0][0])
        ram = int(i.flavor.split("|")[1][0: -2])
        host_price_detail["name"] = i.name
        host_price_detail["flavor"] = i.flavor
        host_price_detail["create_time"] = i.create_time
        host_price_detail["del_time"] = i.delete_time
        c_time = i.create_time
        d_time = i.delete_time
        if month_begin <= c_time < month_end:
            if d_time:
                if d_time >= month_end:
                    during_day = (month_end-c_time).days
                else:
                    during_day = (d_time - c_time).days
            else:
                during_day = (month_end - c_time).days
        elif c_time < month_begin:
            if d_time:
                if d_time >= month_end:
                    during_day = (month_end-month_begin).days
                elif d_time <= month_begin:
                    during_day = -1
                else:
                    during_day = (d_time - month_begin).days
            else:
                during_day = (month_end - month_begin).days
        else:
            during_day = -1
        if during_day != -1:
            cpu_price = float(Price["cpu"]) / 30 * during_day * cpu
            ram_price = float(Price["ram"]) / 30 / 1024 * during_day * ram
            ins_price = float(Price["instance"]) / 30 * during_day
            total_price = cpu_price + ram_price + ins_price
            host_price_detail["price"] = round(total_price, 2)

            host_list.append(host_price_detail)

    return render_to_response("pages/metering/instance_price_detail.html",
                              {"host_list": host_list,
                               "current_user": user})


# 磁盘价格计算明细
def volume_metering_detail(request, y, m):
    user = request.user
    year = int(y)
    month = int(m)
    month_begin = datetime.datetime(year=year, month=month, day=1, hour=0, minute=0, second=0, tzinfo=pytz.utc)
    if month == datetime.datetime.today().month and year == datetime.datetime.today().year:
        month_end = datetime.datetime.now(pytz.utc)
    else:
        if month == 12:
            month_end = datetime.datetime(year=year+1, month=1, day=1,
                                          hour=0, minute=0, second=0, tzinfo=pytz.utc)-datetime.timedelta(days=1)
        else:
            month_end = datetime.datetime(year=year, month=month+1, day=1,
                                          hour=0, minute=0, second=0, tzinfo=pytz.utc)-datetime.timedelta(days=1)
    vol_list = []
    for vol in voldb.Volume.objects.filter(user_id=user.id):
        vol_price_detail = {}
        vol_size = vol.size
        vol_price_detail["name"] = vol.name
        vol_price_detail["size"] = vol_size
        vol_price_detail["create_time"] = vol.create_date
        vol_price_detail["del_time"] = vol.deleted_date

        c_time = vol.create_date
        d_time = vol.deleted_date
        if month_begin <= c_time < month_end:
            if d_time:
                if d_time >= month_end:
                    during_day = (month_end-c_time).days
                else:
                    during_day = (d_time - c_time).days
            else:
                during_day = (month_end - c_time).days
        elif c_time < month_begin:
            if d_time:
                if d_time >= month_end:
                    during_day = (month_end-month_begin).days
                elif d_time <= month_begin:
                    during_day = -1
                else:
                    during_day = (d_time - month_begin).days
            else:
                during_day = (month_end - month_begin).days
        else:
            during_day = -1
        if during_day != -1:
            vol_price = float(Price["volume"])/30 * vol_size * during_day
            vol_price_detail["price"] = round(vol_price, 2)
            vol_list.append(vol_price_detail)

    return render_to_response("pages/metering/volume_price_detail.html",
                              {"vol_list": vol_list, "current_user": user})


# 定义solarwinds数据库同步过来的外部资源计费方法，逻辑与云主机计费相同
def solarwinds_metering(request):
    user = request.user
    now_month_start = datetime.date(datetime.datetime.now().year, datetime.datetime.now().month, 1)
    solarwinds_total_cpu = 0
    solarwinds_total_ram = 0
    solarwinds_total_disk = 0
    solarwinds_total_swins = 0
    solarwinds_cpu_total_price = 0.0
    solarwinds_ram_total_price = 0.0
    solarwinds_disk_total_price = 0.0
    swins_total_price = 0
    for swins in solarwindsdb.Server.objects.filter(tenant_name_id=user.id):
        cpu = int(swins.CPU.split('x')[0])
        ram = int(swins.Mem.__str__()[0])
        disk = eval(swins.TotalHardDisk.rstrip('G').replace('x', '*'))
        c_time = swins.create_time
        if c_time > now_month_start:
            if swins.delete_time:
                d_time = swins.delete_time
                during_day = (d_time - c_time).days
            else:
                today = datetime.datetime.now()
                during_day = (today-c_time).days
        elif swins.delete_time:
            d_time = swins.delete_time
            if d_time > now_month_start:
                during_day = d_time - now_month_start

            else:
                continue
        else:
            today = datetime.datetime.now()
            during_day = today - now_month_start

        solarwinds_total_cpu += cpu
        solarwinds_total_ram += ram
        solarwinds_total_disk += disk
        solarwinds_total_swins += 1
        solarwinds_cpu_price = float(Price["cpu"]) / 30 * during_day.days * cpu
        solarwinds_ram_price = float(Price["ram"]) / 30 / 1024 * during_day.days * ram
        solarwinds_disk_price = float(Price["volume"]) / 30 * during_day.days * disk
        solarwinds_swins_price = float(Price["instance"]) / 30 * during_day.days
        solarwinds_cpu_total_price += solarwinds_cpu_price
        solarwinds_ram_total_price += solarwinds_ram_price
        solarwinds_disk_total_price += solarwinds_disk_price
        swins_total_price += solarwinds_swins_price

    return solarwinds_total_disk, solarwinds_total_ram, solarwinds_total_cpu, solarwinds_total_swins,\
           solarwinds_cpu_total_price, solarwinds_ram_total_price, solarwinds_disk_total_price, \
           swins_total_price