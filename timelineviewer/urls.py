from django.conf.urls import patterns, url

from timelineviewer import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index')
)