# coding:utf8
"""
Django settings for xcloud project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import ldap
from django_auth_ldap.config import LDAPSearch, MemberDNGroupType
from local_settings import *


BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'jq5$-bf*qtys042w##63hsla1-8@xx1lbsbsm4tx-emsh4laq_'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = (
    'suit',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'bootstrap_toolkit',
    'xcloud',
    'account',
    'feature',
    'feature.celerytask',
    'djcelery',
    'django_auth_ldap',
    'feature.volume',
    'feature.instance',
    'feature.solarwinds',
    'feature.serverlist',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'xcloud.urls'

WSGI_APPLICATION = 'xcloud.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

# DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.sqlite3',
#        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#    }
# }

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR,  'templates'),
)


# ldap
AUTH_LDAP_CONNECTION_OPTIONS = {ldap.OPT_REFERRALS: 0}

# 查询用户
AUTH_LDAP_USER_DN_TEMPLATE = "uid=%(user)s,cn=users,dc=enn,dc=com"

# 查找组
AUTH_LDAP_GROUP_SEARCH = LDAPSearch("cn=cloud,cn=groups, dc=enn, dc=com",
                                    ldap.SCOPE_SUBTREE, "(objectClass=groupOfUniqueNames)"
                                    )

AUTH_LDAP_GROUP_TYPE = MemberDNGroupType(member_attr='uniquemember', name_attr='cn')

# 设置组权限
AUTH_LDAP_REQUIRE_GROUP = "cn=cloud,cn=groups,dc=enn,dc=com"
# AUTH_LDAP_DENY_GROUP = "cn=cloud,cn=groups,dc=enn,dc=com"

'''
# 验证 Django 的 User 的is_staff，is_active，is_superuser
AUTH_LDAP_USER_FLAGS_BY_GROUP = {
    "is_staff": "cn=cloud,cn=groups,dc=enn,dc=com",
    "is_active": "cn=cloud,cn=groups,dc=enn,dc=com",
    "is_superuser": "cn=cloud,cn=groups,dc=enn,dc=com",
}
'''

# 把LDAP中用户条目的属性 映射到 Django 的User
AUTH_LDAP_USER_ATTR_MAP = {
    "username": "uid",
    "password": "userPassword",
    "first_name": "givenName",
    "last_name": "sn",
    "email": "mail",
}
AUTH_LDAP_PROFILE_ATTR_MAP = {
    "mobile": "employeeNumber"
}

# 当这个值为 True， LDAP的用户条目映射并创建 Django User 的时候，会自动映创建Group
AUTH_LDAP_MIRROR_GROUPS = True
# 是否每次都从LDAP 把用户信息 更新到 Django 的User
AUTH_LDAP_ALWAYS_UPDATE_USER = True
# 如果为True， LDAPBackend将提供基于LDAP组身份验证的用户属于的组的权限
AUTH_LDAP_FIND_GROUP_PERMS = True
# 如果为True，LDAP组成员将使用Django的缓存框架。
AUTH_LDAP_CACHE_GROUPS = True
# 缓存时长
AUTH_LDAP_GROUP_CACHE_TIMEOUT = 1800

AUTH_LDAP_BIND_AS_AUTHENTICATING_USER = True

# 设置使用 LDAPBackend
AUTHENTICATION_BACKENDS = (
    'django_auth_ldap.backend.LDAPBackend',
    'django.contrib.auth.backends.ModelBackend',
)


# suit conf
from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS as TCP

TEMPLATE_CONTEXT_PROCESSORS = TCP + (
    'django.core.context_processors.request',
)

SUIT_CONFIG = {
    'ADMIN_NAME': '新智云后台管理'
}


