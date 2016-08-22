__author__ = 'songjunting'
from django.db import models
from django.contrib.auth.models import User
from feature.serverlist.models import MetringGroup

class Instance(models.Model):
    instance_id = models.CharField(max_length=40, null=True)
    name = models.CharField(max_length=20)
    tenant_name = models.ForeignKey(User)
    flavor = models.CharField(max_length=30)
    image = models.CharField(max_length=30)
    network = models.CharField(max_length=30)
    public_ip = models.CharField(max_length=30, null=True)
    metering_group = models.ForeignKey(MetringGroup)
    describe = models.CharField(max_length=50, null=True)
    create_time = models.DateTimeField()
    deadline = models.DateTimeField(null=True)
    delete_time = models.DateTimeField(null=True)
    type = models.CharField(max_length=20)

    class Meta:
        db_table = "instance"
        verbose_name = "instance"
        verbose_name_plural = "instance"
