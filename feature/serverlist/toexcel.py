# coding:utf8
import datetime
# from django.http import HttpResponse
from openpyxl import Workbook
# from openpyxl.chart import AreaChart, Reference
import sys, os
sys.path.append('D:/svn/Openstack/SourceCode/xcloud')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xcloud.settings")
from feature.serverlist import models as info


def create_excel():
    hosts = info.Server.objects.all()
    print len(hosts)
    # for i in Server.objects.all():
    wb = Workbook()
    ws = wb.active
    hosts_info = [['计算机名', 'IP地址', '应用名', '应用角色', '操作系统', '硬盘容量', 'CPU核心数量', '内存', '服务类别']]
    for host in hosts:
        host_info = [host.hostname, host.ip, host.appname, host.appRole, host.OS, host.HardDisk, host.CPU, host.Mem, host.type]
        hosts_info.append(host_info)
    # print hosts_info

    for row in hosts_info:
        ws.append(row)
    '''
    chart = AreaChart()
    chart.title = "Area Chart"
    chart.style = 13
    chart.x_axis.title = 'Test'
    chart.y_axis.title = 'Percentage'

    cats = Reference(ws, min_col=1, min_row=1, max_row=7)
    data = Reference(ws, min_col=1, min_row=1, max_col=1, max_row=7)
    chart.add_data(data, titles_from_data=True)
    chart.set_categories(cats)

    ws.add_chart(chart, "A10")
    '''
    filename = str(datetime.datetime.now()).split('.')[0].replace(' ', '_').replace(':', '-')

    wb.save("d:/tmp/%s.xlsx" % filename)
    # return HttpResponse("success")


if __name__ == '__main__':

    create_excel()