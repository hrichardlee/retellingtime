from django.conf.urls import patterns, url

from timelinedata import views

urlpatterns = patterns('',
    url(r'^search/(?P<page_title>.+)/$', views.search),
    url(r'^(?P<id>\d+)/$', views.detail),
    url(r'^$', views.all, name='all')
)