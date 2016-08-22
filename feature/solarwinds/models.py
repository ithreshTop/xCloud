#!usr/bin/env python
# coding:utf-8
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
'''
class UserInfo(models.Model):
    username = models.CharField(max_length=50)
    email = models.EmailField(max_length=30, unique=True)
    phone = models.CharField(max_length=11, blank=True, null=True)
    IndustryGroupName = models.ManyToManyField('IndustryGroup')

    def __unicode__(self):
        return self.username

    class Meta:

        verbose_name = '用户信息'
        verbose_name_plural = '用户信息'

class IndustryGroup(models.Model):
    name = models.CharField(u'产业集团', max_length=50, unique=True, blank=True, null=True)

    class Meta:

        verbose_name = '产业集团'
        verbose_name_plural = '产业集团'

    def __unicode__(self):
        return self.name
'''


class Asset(models.Model):
    nodesid = models.IntegerField(u'节点ID', null=True)
    hostname = models.CharField(u'主机名', max_length=256, blank=True, null=True)
    ip = models.GenericIPAddressField(u'IP地址', blank=True, null=True)
    TotalHardDisk = models.CharField(u'总硬盘容量', max_length=10, blank=True, null=True)
    Mem = models.CharField(u'内存', max_length=5, blank=True, null=True)
    CPU = models.CharField(u'CPU核心数量', max_length=10, blank=True, null=True)
    create_time = models.DateField(u'资源创建时间', max_length=30, null=True)
    delete_time = models.DateField(u'资源删除时间', max_length=30, null=True)
    tenant_name = models.ForeignKey(User)
    classify_choices = ((u'enn_nsd', u'enn_sso'), (u'enn_nsd', u'enn_sso'))
    classify = models.CharField(u'分类', default='enn_sso', choices=classify_choices, max_length=10, blank=True, null=True)
    mttype_choices = ((u'宿主机', u'IBM X3850X5 7143T2K'), (u'vm', u'vm'),)
    mttype = models.CharField(u'设备类型', choices=mttype_choices, max_length=20, blank=True, null=True)
    sn = models.CharField(u'SN号', max_length=10, unique=True, blank=True, null=True)
    # appName = models.CharField(u'应用名称', max_length=30, blank=True, null=True)
    # appRole = models.CharField(u'应用角色', max_length=30, blank=True, null=True)
    # fibrechannelhbaCards = models.NullBooleanField(u'光纤通道卡', default=False, blank=True, null=True)
    # fiberswitchport = models.CharField(u'光纤交换机端口', max_length=30, blank=True, null=True)
    MangeIP = models.GenericIPAddressField(u'管理IP', blank=True, null=True)
    Cabinet = models.CharField(u'机柜位置', max_length=10, blank=True, null=True)
    # OS_choices = ((u'Windows', u'Windows'), (u'linux', u'Linux'))
    # OS = models.CharField(u'操作系统', choices=OS_choices, max_length=50, blank=True, null=True)
    # OsVersion_choices = ((u'Win2008R2', u'Windows server 2008 R2'), (u'1504', u'Linux1504'),)
    # OsVersion = models.CharField(u'操作系统版本号', choices=OsVersion_choices, max_length=10, blank=True, null=True)
    Cluster = models.NullBooleanField(u'集群', default=False, blank=True, null=True)
    # HardDisk = models.CharField(u'硬盘容量', max_length=10, blank=True, null=True)
    # CpuMainFrequency = models.CharField(u'CPU主频', max_length=10, blank=True, null=True)
    Domain_choices = ((u'xinao', u'addom.xinaogroup.com'), (u'test', u'test.com'))
    Domain = models.CharField(u'域信息', choices=Domain_choices, max_length=20, blank=True, null=True)
    Raid_choices = ((u'1', u'raid1'), (u'2', u'raid2'), (u'0', u'raid0'), (u'0+1', u'raid0+1'),)
    Raid = models.CharField(u'磁盘阵列信息', choices=Raid_choices, max_length=10, blank=True, null=True)
    PriAdmin = models.CharField(u'第一管理员', max_length=10, blank=True, null=True)
    SecAdmin = models.CharField(u'第二管理员', max_length=10, blank=True, null=True)
    # UserInfo = models.ForeignKey(UserInfo, verbose_name='用户信息')
    # Dmz = models.NullBooleanField(u'是否DMZ发布', default=False, blank=True, null=True)
    DataCenterAddress_choices = ((u'廊坊', u'lf'), (u'北京', u'bj'),)
    DataCenterAddress = models.CharField(u'数据中心', choices=DataCenterAddress_choices, max_length=10, blank=True, null=True)
    # CreateTime = models.DateField(u'资源交付时间', max_length=10, blank=True, null=True)
    # IndustryGroupName = models.ForeignKey(IndustryGroup, verbose_name='产业集团', blank=True, null=True)
    # CompanyName = models.CharField(u'公司', max_length=20, blank=True, null=True)

    class Meta:

        verbose_name = '主机'
        verbose_name_plural = '主机'

    def __unicode__(self):
        return self.hostname    # 这段admin首页显示models的表

