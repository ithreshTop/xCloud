from django.conf.urls import patterns, include, url
from django.contrib import admin
from account import views
from feature.network_topolopy.views import JSONView
urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'cloud.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),


    url(r'^changePassword/$', 'feature.profiles.views.changePassword'),

    # url(r'^base/$', include('feature.volume.urls')),
    # test zone
    url(r'^$', 'feature.overview.views.overview'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/login/$', 'account.views.Login'),
    url(r'^regist/$', 'account.views.regist'),
    url(r'^logout/$', 'account.views.Logout'),
	url(r'^feature/', include('feature.urls')),
	url(r'^regist/ajax/$','account.views.ajax_process'),
	url(r'^changepwd/$','account.views.changepwd'),
    url(r'^base/(.)$', 'xcloud.views.jump'),
    url(r'^nettopo/$',JSONView.as_view(),name="json")
)

handler404 = views.not_found
handler500 = views.server_error