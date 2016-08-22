# coding:utf8
__author__ = 'syx'

# HostMachine对应配置
# 操作系统类型选择 u'db',u'admin'
OS_choices = (
    (u'Microsoft Windows', u'Microsoft Windows'),
    (u'Linux', u'Linux'),
    (u'VMware ESX Server', u'VMware ESX Server'),
)
OsVersion_choices = (
    (u'CentOS 5_x64', u'CentOS 5 (64位)'),
    (u'CentOS 5.8_x64', u'CentOS 5.8 (64位)'),
    (u'CentOS 7_x64', u'CentOS 7 (64位)'),
    (u'CentOS 6.5_x64', u'CentOS 6.5 (64位)'),
    (u'CentOS 6.7_x64', u'CentOS 6.7 (64位)'),
    (u'Linux定制', u'Linux定制'),
    (u'Microsoft Windows 7', u'Microsoft Windows 7'),
    (u'Microsoft Windows Server 2003', u'Microsoft Windows Server 2003'),
    (u'Microsoft Windows Server 2008', u'Microsoft Windows Server 2008'),
    (u'Microsoft Windows Server 2008 R2', u'Microsoft Windows Server 2008 R2'),
    (u'Microsoft Windows XP Professional', u'Microsoft Windows XP Professional'),
    (u'RHEL 6.5_x64', u'RHEL 6.5_x64'),
    (u'RHEL 5.4_x64', u'RHEL 5.4_x64'),
    (u'Ubuntu 12_x64', u'Ubuntu 12_x64'),
    (u'Ubuntu Linux_x64', u'Ubuntu Linux_x64'),
    (u'ESXI 5.0', u'ESXI 5.0'),
    (u'ESXI 5.1 U3', u'ESXI 5.1 U3'),
    (u'Ubuntu Linux_x64', u'Ubuntu Linux_x64'),
)
classify_choices = (
    (u'test', u'测试'),
    (u'pro', u'生产'),
)

# server对应配置
# 主机类型，物理机or vm
mttype_choices = (
    (u'宿主机', u'12'),
    (u'vm', u'vm'),
)
# 应用服务类别--生产or测试环境
type_choices = (
    (u'pro', u'生产'),
    (u'dev_test', u'开发测试'),
    (u'lib', u'实验'),
)
'''
OS_choices = ((u'Windows', u'Windows'), (u'linux', u'Linux'))
OsVersion_choices = ((u'Win2008R2', u'Windows server 2008 R2'), (u'1504', u'Linux1504'),)
'''
# raid类型
Raid_choices = ((u'1', u'raid1'),
                (u'2', u'raid2'),
                (u'5', u'raid5'),
                (u'0', u'raid0'),
                (u'0+1', u'raid0+1')
                )
# 设备类型
classify_choices = (
    (u'enn_nsd', u'网络设备'),
    (u'enn_nso', u'服务器'),
)
# 域属性
Domain_choices = (
    (u'addom.xinaogroup.com', u'addom.xinaogroup.com'),
    (u'adlab.xinaogroup.com', u'adlab.xinaogroup.com'),
    (u'test.xinaogroup.com', u'test.xinaogroup.com'),
)
# 数据中心物理位置位置
DataCenterAddress_choices = (
    (u'0316001', u'廊坊数据中心1号库房'),
    (u'0316002', u'廊坊数据中心2号库房'),
    (u'0316003', u'廊坊数据中心3号库房'),
    (u'0316004', u'廊坊数据中心主机房'),
    (u'0316004', u'廊坊智能大厦数据中心主机房'),
    (u'0010001', u'北京亦庄数据中心主机房'),
    (u'0010002', u'北京燕郊数据中心主机房'),
)

# 产业集团
MeteringGroup_choices = (
    (u'新智云', u'新智云'),
    (u'E城E家', u'E城E家'),
    (u'E城到家', u'E城到家'),
    (u'北部湾旅游', u'北部湾旅游'),
    (u'财务公司', u'财务公司'),
    (u'集团总部', u'集团总部'),
    (u'能源分销', u'能源分销'),
    (u'能源研究院', u'能源研究院'),
    (u'太阳能源', u'太阳能源'),
    (u'威远生化', u'威远生化'),
    (u'新博卓创', u'新博卓创'),
    (u'新博卓畅', u'新博卓畅'),
    (u'新地工程', u'新地工程'),
    (u'新绎地产', u'新绎地产'),
    (u'新绎健康', u'新绎健康'),
    (u'新苑阳光', u'新苑阳光'),
    (u'新智互联网', u'新智互联网'),
    (u'智能能源', u'智能能源'),
)

# CMDB数据中心资产管理

# 维保单位信息
maintenance_group_choice = (
    (u'szsm', u'神州数码'),
    (u'zj', u'中集'),
)

# 资产状态
asset_status_choices = (
    (u'in_use', u'在用'),
    (u'in_loan', u'借出'),
    (u'in_service', u'维修'),
    (u'in_idle', u'闲置'),
    (u'check_out', u'出库'),
    (u'retirement', u'报废'),
)

# 资产来源
asset_befrom_choices = (
    (u'borrow', u'借用'),
    (u'rent', u'租用'),
    (u'self_buying', u'自购'),
    (u'other', u'其他'),
)

# 资产类型
asset_type_choices = (
    (u'server', u'服务器'),
    (u'router', u'路由'),
    (u'switch', u'交换机'),
    (u'Firewall', u'防火墙'),
    (u'storage', u'存储设备'),
    (u'minicomputer', u'小型机'),
    #(u'ups', u'ups'),
    # 小型机
)

#工具类型
tools_name_choices = (
    (u'cable', u'网线'),
    (u'fiber', u'光纤'),
    (u'tools', u'工具'),
    (u'other', u'其他工具'),
)

# 磁带类型
tape_type_choices = (
    (u'clean_tape', u'清洗带'),
    (u'tape', u'磁带'),
)