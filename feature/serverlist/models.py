#!usr/bin/env python
# coding:utf-8
from django.db import models
from django.contrib.auth.models import User
import sys
from settings import *
import uuid


reload(sys)
sys.setdefaultencoding('utf8')

# Create your models here.

class VspherePool(models.Model):
    pool_name = models.CharField(u'资源池', max_length=20, unique=True)
    pool_id = models.CharField(u'资源池ID', max_length=20, primary_key=True, unique=True)
    pool_desc = models.CharField(u'描述', max_length=20, null=True)
    born_time = models.DateTimeField(u'创建时间', auto_now_add=True, editable=False, blank=True, null=True)
    update_time = models.DateTimeField(u'上次修改时间', auto_now=True, editable=True, blank=True, null=True)
    # poll_address = models.CharField(u'位置', choices=DataCenterAddress_choices, max_length=10, null=True, blank=True)

    class Meta:

        verbose_name = '资源池'
        verbose_name_plural = '资源池'

    def __unicode__(self):
        return self.pool_name


class Maintenance(models.Model):
    maintenance_group = models.CharField(u'维保单位', max_length=30, primary_key=True)
    phone = models.CharField(u'报修电话', max_length=30)
    contact = models.CharField(u'联系人', max_length=50, null=True, blank=True)
    born_time = models.DateTimeField(u'创建时间', auto_now_add=True, editable=False, blank=True, null=True)
    update_time = models.DateTimeField(u'上次修改时间', auto_now=True, editable=True, blank=True, null=True)

    class Meta:

        verbose_name = '维保单位'
        verbose_name_plural = '维保单位'

    def __unicode__(self):
        return self.maintenance_group



class HostMachine(models.Model):
    machine_type = models.CharField(u'物理机型号', max_length=30, blank=True, null=True)
    hostname = models.CharField(u'物理主机名', max_length=255, null=True, unique=True)
    sn = models.CharField(u'SN号', max_length=50, blank=True, null=True, unique=True)
    ip = models.GenericIPAddressField(u'物理主机IP地址')
    app_name = models.CharField(u'主机应用名称', max_length=100, blank=True, null=True)
    app_description = models.CharField(u'主机应用描述', max_length=100, blank=True, null=True)
    Cabinet = models.CharField(u'机柜位置', max_length=10, blank=True, null=True)
    OS = models.CharField(u'操作系统', choices=OS_choices, max_length=50, blank=True, null=True)
    OsVersion = models.CharField(u'操作系统版本号', choices=OsVersion_choices, max_length=10, blank=True, null=True)
    Cluster = models.NullBooleanField(u'集群', default=False, blank=True, null=True)
    TotalHardDisk = models.CharField(u'总硬盘容量', max_length=10, blank=True, null=True)
    CPU = models.CharField(u'CPU核心数量', max_length=10, blank=True, null=True)
    CpuMainFrequency = models.CharField(u'CPU主频', max_length=10, blank=True, null=True)
    mem = models.IntegerField(u'内存', null=True, blank=True)
    Raid = models.CharField(u'磁盘阵列信息', choices=Raid_choices, max_length=10, blank=True, null=True)
    fibrechannelhbacards = models.NullBooleanField(u'光纤通道卡', default=False, blank=True, null=True)
    fiberswitchport = models.CharField(u'光纤交换机端口', max_length=30, blank=True, null=True)
    MangeIP = models.GenericIPAddressField(u'管理IP', blank=True, null=True)
    Domain = models.CharField(u'域信息', choices=Domain_choices, max_length=20, blank=True, null=True)
    app_user = models.ForeignKey(User, verbose_name='应用管理员', related_name='app_user', null=True)
    PriAdmin = models.ForeignKey(User, verbose_name='管理员', related_name='admin', null=True)
    dmz = models.NullBooleanField(u'DMZ', default=False)
    pool = models.ForeignKey(VspherePool, verbose_name='资源池')
    type = models.CharField(u'应用服务类别', choices=type_choices, max_length=10)
    delivery_time = models.DateField(u'资源交付时间')
    datacenter_address = models.CharField(u'位置', max_length=10, null=True, blank=True)
    born_time = models.DateTimeField(u'创建时间', auto_now_add=True, editable=False, blank=True, null=True)
    update_time = models.DateTimeField(u'上次修改时间', auto_now=True, editable=True, blank=True, null=True)
    '''
    produced_time = models.DateField(u'生产时间')
    maintenance_cycle = models.IntegerField(u'维保周期')
    later_maintenance_time = models.DateField(u'上次维保时间')
    maintenance_group = models.ForeignKey(Maintenance)
    '''
    class Meta:

        verbose_name = '宿主机'
        verbose_name_plural = '宿主机'

    def __unicode__(self):
        return self.hostname



class Server(models.Model):
    hostname = models.CharField(u'主机名', max_length=255, null=True, unique=True)
    ip = models.GenericIPAddressField(u'IP地址')
    appname = models.CharField(u'应用名称', max_length=30, blank=True, null=True)
    appRole = models.CharField(u'应用角色', max_length=30, blank=True, null=True)
    type = models.CharField(u'类别', choices=type_choices, max_length=10, blank=True, null=True)
    appdescription = models.CharField(u'应用描述', max_length=100, blank=True, null=True)
    OS = models.CharField(u'操作系统', choices=OS_choices, max_length=50, blank=True, null=True)
    OsVersion = models.CharField(u'操作系统版本号', choices=OsVersion_choices, max_length=50, blank=True, null=True)
    Cluster = models.NullBooleanField(u'集群', default=False, blank=True, null=True)
    pool_id = models.ForeignKey(VspherePool, verbose_name='资源池')
    HardDisk = models.CharField(u'硬盘容量', max_length=10, blank=True, null=True)
    TotalHardDisk = models.CharField(u'总硬盘容量', max_length=10, blank=True, null=True)
    CPU = models.IntegerField(u'CPU核心数量', blank=True, null=True)
    # CpuMainFrequency = models.CharField(u'CPU主频', max_length=10, blank=True, null=True)
    Mem = models.CharField(u'内存', max_length=5, blank=True, null=True)
    # Raid = models.CharField(u'磁盘阵列信息', choices=Raid_choices, max_length=10, blank=True, null=True)
    Domain = models.CharField(u'域信息', choices=Domain_choices, max_length=20, blank=True, null=True)
    PriAdmin = models.ForeignKey(User, related_name='priadmin', null=True)
    tenant_name = models.ForeignKey(User, related_name='appuserinfo', null=True)
    create_time = models.DateField(u'资源交付时间', max_length=20, null=True)
    delete_time = models.DateField(u'资源删除时间', max_length=20, blank=True, null=True)
    IndustryGroupName = models.CharField(verbose_name='计费组', max_length=30, choices=MeteringGroup_choices, null=True)
    born_time = models.DateTimeField(u'创建时间', auto_now_add=True, editable=False, blank=True, null=True)
    update_time = models.DateTimeField(u'上次修改时间', auto_now=True, editable=True, blank=True, null=True)
    # CompanyName = models.CharField(u'公司', max_length=20, blank=True, null=True)

    class Meta:

        verbose_name = '主机'
        verbose_name_plural = '主机'

    def __unicode__(self):
        return self.hostname    # 这段admin首页显示models的表


class Asset(models.Model):
    uid = models.UUIDField('资产编号', default=uuid.uuid1, auto_created=True, editable=False)
    type = models.CharField('设备类型', max_length=20, null=True, blank=True)
    product_model = models.CharField('产品型号', max_length=100, null=True, blank=True)
    sn = models.CharField('SN号', max_length=50, null=True, blank=True)
    name = models.CharField('设备名称', max_length=50, null=True, blank=True)
    cabinet = models.CharField('机柜位置', max_length=100, null=True, blank=True)
    location = models.CharField('存放位置', max_length=50, null=True, blank=True)
    status = models.CharField('资产状态', max_length=20, choices=asset_status_choices, blank=True)
    be_from = models.CharField('资产来源', max_length=20, choices=asset_befrom_choices, blank=True)
    maintenance_cycle = models.IntegerField('维保周期', null=True, blank=True)
    later_maintenance_time = models.DateField('上次维保日期', null=True, blank=True)
    maintenance_group = models.ForeignKey(Maintenance, max_length=30, verbose_name='维保单位', null=True)
    maintenance_phone = models.CharField('维保电话', max_length=20, null=True, blank=True)
    approach_date = models.DateField('入场时间', null=True, blank=True)
    out_time = models.DateField('出场时间', null=True, blank=True)
    vendor = models.CharField('生产厂商', max_length=50, null=True, blank=True)
    num_power = models.IntegerField('电源数量', null=True, blank=True)
    eth_connection = models.CharField('设备网口连接情况', max_length=100, null=True, blank=True)
    purchase_date = models.DateField('采购日期', null=True, blank=True)
    asset_admin = models.ForeignKey(User, verbose_name='管理员', related_name='asset_admin')
    app_admin = models.ForeignKey(User, verbose_name='应用负责人', related_name='asset_app_admin')
    mark = models.CharField('备注', max_length=100, null=True, blank=True)
    maintenance_buy_date = models.DateField('维保采购日期', null=True, blank=True)
    maintenance_date = models.DateField('维保到期日', null=True, blank=True)
    born_time = models.DateTimeField(u'创建时间', auto_now_add=True, editable=False, blank=True, null=True)
    update_time = models.DateTimeField(u'上次修改时间', auto_now=True, editable=True, blank=True, null=True)

    class Meta:

        verbose_name = '资产'
        verbose_name_plural = '资产'

class Equipment(models.Model):
    uid = models.UUIDField('辅助设备资产编号', default=uuid.uuid1, auto_created=True, editable=False)
    name = models.CharField('设备名称', max_length=50)
    number = models.IntegerField('数量', null=True)
    type = models.CharField('设备型号', max_length=50, null=True)
    sn = models.CharField('SN号', max_length=50, null=True)
    maintenance_cycle = models.IntegerField('维保周期', null=True, blank=True)
    later_maintenance_time = models.DateField('上次维保日期', null=True, blank=True)
    maintenance_group = models.ForeignKey(Maintenance, max_length=30, null=True, blank=True)
    maintenance_buy_date = models.DateField('维保采购日期', null=True, blank=True)
    maintenance_date = models.DateField('维保到期日', null=True, blank=True)
    maintenance_phone = models.CharField('维保电话', max_length=20, null=True, blank=True)
    mark = models.CharField('备注', max_length=100, null=True, blank=True)
    born_time = models.DateTimeField(u'创建时间', auto_now_add=True, editable=False, blank=True, null=True)
    update_time = models.DateTimeField(u'上次修改时间', auto_now=True, editable=True, blank=True, null=True)

    class Meta:

        verbose_name = '辅助设备'
        verbose_name_plural = '辅助设备'

class Tools(models.Model):
    uid = models.UUIDField('工具资产编号', default=uuid.uuid1, auto_created=True, editable=False)
    name = models.CharField('工具类型', choices=tools_name_choices, max_length=20, null=True, blank=True)
    standard = models.CharField('规格', max_length=20, null=True, blank=True)
    type = models.CharField('型号', max_length=50, null=True, blank=True)
    length = models.IntegerField('长度', null=True, blank=True)
    count = models.IntegerField('数量', null=True, blank=True)
    mark = models.CharField('备注', max_length=100, null=True, blank=True)
    born_time = models.DateTimeField(u'创建时间', auto_now_add=True, editable=False, blank=True, null=True)
    update_time = models.DateTimeField(u'上次修改时间', auto_now=True, editable=True, blank=True, null=True)

    class Meta:

        verbose_name = '工具'
        verbose_name_plural = '工具'


class MetringGroup(models.Model):
    group_name = models.CharField(u'计费组', max_length=50, unique=True)
    group_id = models.CharField(u'组ID', max_length=10, unique=True)
    born_time = models.DateTimeField(u'创建时间', auto_now_add=True, editable=False, blank=True, null=True)
    update_time = models.DateTimeField(u'上次修改时间', auto_now=True, editable=True, blank=True, null=True)

    class Meta:

        verbose_name = '计费组'
        verbose_name_plural = '计费组'

    def __unicode__(self):
        return self.group_name

class Tape(models.Model):
    uid = models.UUIDField('磁带编号', default=uuid.uuid1, auto_created=True, editable=False)
    type = models.CharField('磁带类型', max_length=50, choices=tape_type_choices)
    model = models.CharField('磁带型号', max_length=50)
    SN = models.CharField('SN号', max_length=50)
    data_name = models.CharField('保存数据的名称', max_length=200, blank=True)
    data_cycle = models.CharField('数据保存周期', max_length=200, blank=True)
    data_for_section = models.CharField('数据使用部门', max_length=50, blank=True)
    tape_of_section = models.CharField('磁带归属部门', max_length=50, blank=True)
    data_admin = models.ForeignKey(User, related_name='data_admin', verbose_name='数据管理员')
    maintenance = models.ForeignKey(Maintenance, related_name='main_group', verbose_name='维保单位')
    in_time = models.DateField('磁带进场时间', blank=True)
    out_time = models.DateField('磁带出场时间', blank=True)
    vendor = models.CharField('生产厂商', max_length=50, blank=True)
    purchase_date = models.DateField('采购日期', blank=True)
    location = models.CharField('磁带存放位置', choices=DataCenterAddress_choices, max_length=50, blank=True)
    status = models.CharField('磁带状态', choices=asset_status_choices, max_length=50, blank=True)
    be_from = models.CharField('磁带来源', choices=asset_befrom_choices, max_length=50, blank=True)
    born_time = models.DateTimeField(u'创建时间', auto_now_add=True, editable=False, blank=True, null=True)
    update_time = models.DateTimeField(u'上次修改时间', auto_now=True, editable=True, blank=True, null=True)

    class Meta:

        verbose_name = '磁带'
        verbose_name_plural = '磁带'

    def __unicode__(self):
        return self.SN