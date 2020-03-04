from django.conf.urls import url

from . import views

app_name = 'fermenter'
urlpatterns = [
  url(r'^list/$', views.ListView.as_view(), name='list'),
  url(r'^(?P<pk>[0-9]+)/$', views.DetailView.as_view(), name='detail'),
  url(r'^(?P<pk>[0-9]+)/edit/$', views.edit, name='edit'),
  url(r'^(?P<pk>[0-9]+)/new_beer/$', views.new_beer, name='new_beer'),
  url(r'^(?P<pk>[0-9]+)/get_temperature/$', views.get_temperature, name='get_temperature'),
  url(r'^(?P<pk>[0-9]+)/set_setpoint/$', views.set_setpoint, name='set_setpoint'),
]
