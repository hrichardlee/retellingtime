from django.conf.urls import patterns, url

from timelinedata import views

urlpatterns = patterns('',
    url(r'^(?P<page_title>.+)/$', views.detail, name='detail'),
    url(r'^$', views.all, name='all')
)