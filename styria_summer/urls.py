from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns(
    '',
    # Examples:
    # url(r'^$', 'styria_summer.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^feeddler/', include('feeddler.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
