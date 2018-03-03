from django.conf.urls import url

from . import views

app_name = 'component'
urlpatterns = [
  url(r'^list/$', views.ListView.as_view(), name='list'),
]
