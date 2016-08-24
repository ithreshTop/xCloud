# coding:utf8
from __future__ import absolute_import
from celery.schedules import crontab

# 数据库设置
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'xcloud',
        'USER': 'root',
        'PASSWORD': 'xcloud',
        'HOST': '10.1.1.1',
        'PORT': '3306',
        'TEST_CHARSET': 'utf8',
        'OPTIONS': {
            "init_command": "SET foreign_key_checks=0",
        }
    }
}

# celery broker_url配置
BROKER_URL = "amqp://guest:guest@10.1.1.1:5672/"
CELERYBEAT_SCHEDULE = {'do-task-everyday': {
    'task': 'feature.celerytask.tasks.is_deadline',
    'schedule': crontab(hour=0, minute=0)}, 
    'ldap-update-everyday': {
    'task': 'feature.celerytask.tasks.ldap_update',
    'schedule': crontab(hour=0, minute=0)},}

# ldap 配置
AUTH_LDAP_SERVER_URI = 'ldap://10.37.1.1:389'
AUTH_LDAP_BIND_DN = "cn=root"
AUTH_LDAP_BIND_PASSWORD = "Passw0rd"


# openstack 环境配置
# 生产环境
DATA_CENTER_PRO = {
    "username": "admin",
    "password": "admin",
    "tenant_name": "admin",
    "auth_url": "http://10.1.1.1:5000/v2.0",
}
# 测试环境
DATA_CENTER_TEST = {
    "username": "admin",
    "password": "admin",
    "tenant_name": "admin",
    "auth_url": "http://10.1.1.1:5000/v2.0",
}

# 发送邮件
EMAIL_HOST = '**'
EMAIL_PORT = 25
EMAIL_HOST_USER = '**'

EMAIL_HOST_USER_TLS = True

#导入模块
import logging
import logging.handlers
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
       'standard': {
            'format': '%(asctime)s [%(threadName)s:%(thread)d] [%(name)s:%(lineno)d] [%(module)s:%(funcName)s] [%(levelname)s]- %(message)s'}  #日志格式
    },
    'filters': {
    },
    'handlers': {
        'default': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'D:/tmp/all.log',
            'formatter': 'standard',
        },
    },
    'loggers': {
        'feature': {
            'handlers': ['default'],
            'level': 'INFO',
            'propagate': False,
        },
    }
}