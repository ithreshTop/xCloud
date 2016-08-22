#!usr/bin/env python
# coding:utf-8
from django.contrib import admin
from feature.serverlist import models

'''
# actions = [函数名] 加入到models类中，实现批量下拉操作
def server_copy(modeladmin, request, queryset):
    queryset.update(status='p')
    server_copy.short_description = "批量执行动作"


class SeverStateFilter(admin.SimpleListFilter):
        title = (u'状态')
        parameter_name = 'del_status'

        def lookups(self, request, model_admin):

            return (
                (0, u'正常'),
                (1, u'已删除'),
            )

        def queryset(self, request, queryset):
            if self.value():
                if int(self.value()) == 0:
                    return queryset.filter()
                if int(self.value()) == 1:
                    return queryset.filter()
'''

class MetringGroupAdmin(admin.ModelAdmin):
    list_display = ('group_name',)
    actions_on_top = True
    actions_on_bottom = False

class ServerAdmin(admin.ModelAdmin):
    list_display = ('hostname', 'ip', 'OS', 'appname', 'info_status')
    search_fields = ('hostname', 'ip')
    # radio_fields = {'OS': admin.VERTICAL}
    # actions = [copy]
    actions_on_top = True
    actions_on_bottom = False
    # fields = ('hostname', 'OS', 'ip')  控制字段显隐
    # list_filter = (SeverStateFilter,)  # 筛选控制器

    # 函数可作为admin的显示字段，需要添加到listdisplay
    def info_status(self, obj):
        if obj.delete_time:
            return u'<span style="color:red;font-weight:bold">%s</span>' % (u"已删除",)
        else:
            return u'<span style="color:green;font-weight:bold">%s</span>' % (u"正常",)

    info_status.short_description = u'状态'
    info_status.allow_tags = True

class HostMachineAdmin(admin.ModelAdmin):
    list_display = ('machine_type', 'hostname', 'ip', 'app_description')
    search_fields = ('hostname', 'ip')
    actions_on_top = True
    actions_on_bottom = False

class MaintenanceAdmin(admin.ModelAdmin):
    list_display = ('maintenance_group', 'phone', 'contact')
    actions_on_top = True
    actions_on_bottom = False

class VspherePoolAdmin(admin.ModelAdmin):
    list_display = ('pool_name', 'pool_id', 'pool_desc')
    actions_on_top = True
    actions_on_bottom = False

class AssetAdmin(admin.ModelAdmin):
    list_display = ('type', 'product_model', 'name', 'cabinet', 'sn', 'location', 'status')
    search_fields = ('sn', 'type')
    actions_on_top = True
    actions_on_bottom = False


class EquipmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'sn')
    actions_on_top = True
    actions_on_bottom = False

class ToolsAdmin(admin.ModelAdmin):
    list_display = ('name', 'standard', 'type')
    actions_on_top = True
    actions_on_bottom = False

class TapeAdmin(admin.ModelAdmin):
    list_display = ('type', 'model', 'SN', 'data_name')

# 注册数据库
# admin.site.register(models.UserInfo, UserInfoAdmin)
admin.site.register(models.MetringGroup, MetringGroupAdmin)
admin.site.register(models.Server, ServerAdmin)
admin.site.register(models.HostMachine, HostMachineAdmin)
admin.site.register(models.Maintenance, MaintenanceAdmin)
admin.site.register(models.VspherePool, VspherePoolAdmin)
admin.site.register(models.Asset, AssetAdmin)
admin.site.register(models.Equipment, EquipmentAdmin)
admin.site.register(models.Tools, ToolsAdmin)
admin.site.register(models.Tape, TapeAdmin)