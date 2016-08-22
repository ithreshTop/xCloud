from django.db import models
from django.contrib.auth.models import User
from feature.serverlist.models import MetringGroup

class Volume(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField('Volume name', null=False, blank=False, max_length=128)
    volume_id = models.CharField('OS Volume UUID', null=True, blank=False, max_length=128)
    size = models.IntegerField('Volume size', null=False, blank=False)
    create_date = models.DateTimeField("Create Date")
    deleted_date = models.DateTimeField("Deleted Date", null=True)
    description = models.CharField("Description", max_length=128)
    type = models.CharField("Type", max_length="30")
    metering_group = models.ForeignKey(MetringGroup)
    """
    User info
    """
    user = models.ForeignKey(User)

    def __unicode__(self):
        return u'Profile of volume: %s' % self.user.username

    class Meta:
        db_table = "volume"
        ordering = ['-create_date']
        verbose_name = "Volume"
        verbose_name_plural = "Volume"

class VolumeToServer(models.Model):
    id = models.AutoField(primary_key=True)
    volume_id = models.CharField('volume_id', null=False, blank=False, max_length=30)
    server_id = models.CharField('server_id', null=False, blank=False, max_length=30)

    def __unicode__(self):
        return u'%s to %s' % self.volume_id, self.server_id

    class Meta:
        db_table = "volume_server"