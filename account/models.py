from django.db import models
from django.contrib.auth.models import User
from feature.serverlist.models import MetringGroup


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    mobile = models.CharField(max_length=26, null=True)
    keystone_password = models.CharField(max_length=30, null=True)
    metering_group = models.ForeignKey(MetringGroup, null=True, blank=True)


    def __unicode__(self):
        return u'Profile of user: %s' % self.user.username

    class Meta:
        db_table = "user_profile"
        verbose_name = "UserProfile"
        verbose_name_plural = "UserProfile"