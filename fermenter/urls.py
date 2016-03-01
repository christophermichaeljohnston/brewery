from django.conf.urls import url

from . import views

app_name = 'fermenter'
urlpatterns = [
    url(r'^discover/$', views.discover, name='discover'),
    url(r'^list/$', views.ListView.as_view(), name='list'),
    url(r'^(?P<pk>[0-9]+)/$', views.DetailView.as_view(), name='detail'),
    url(r'^(?P<pk>[0-9]+)/edit/$', views.edit, name='edit'),
    url(r'^(?P<pk>[0-9]+)/chart/$', views.chart, name='chart'),
    url(r'^(?P<pk>[0-9]+)/chart_data/$', views.chart_data, name='chart_data'),
    url(r'^temperatures/$', views.temperatures, name='temperatures'),
]
