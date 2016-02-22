from django.conf.urls import url

from . import views

app_name = 'device'
urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^discover$', views.discover, name='discover'),
]
