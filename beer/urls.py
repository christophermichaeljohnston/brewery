from django.conf.urls import url

from . import views

app_name = 'beer'
urlpatterns = [
  url(r'^list/$', views.ListView.as_view(), name='list'),
  url(r'^create/$', views.create, name='create'),
  url(r'^(?P<pk>[0-9]+)/$', views.DetailView.as_view(), name='detail'),
  url(r'^(?P<pk>[0-9]+)/edit/$', views.edit, name='edit'),
  url(r'^(?P<pk>[0-9]+)/delete/$', views.delete, name='delete'),
  url(r'^(?P<pk>[0-9]+)/start/$', views.start, name='start'),
  url(r'^(?P<pk>[0-9]+)/stop/$', views.stop, name='stop'),
  url(r'^(?P<pk>[0-9]+)/start_ramp/$', views.start_ramp, name='start_ramp'),
  url(r'^(?P<pk>[0-9]+)/stop_ramp/$', views.stop_ramp, name='stop_ramp'),
  url(r'^(?P<pk>[0-9]+)/chart_data/$', views.chart_data, name='chart_data'),
]
