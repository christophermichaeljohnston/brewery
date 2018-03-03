from django.conf.urls import url

from . import views

app_name = 'device'
urlpatterns = [
    url(r'^list/$', views.ListView.as_view(), name='list'),
    url(r'^discover/$', views.discover, name='discover'),
    #url(r'^(?P<pk>[0-9]+)/$', views.DetailView.as_view(), name='detail'),
]
