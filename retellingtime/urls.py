from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^timelinedata/', include('timelinedata.urls')),
    url(r'^viewer/', include('timelineviewer.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
