from django.conf.urls import url

from . import views

app_name = 'equipment'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^discover$', views.discover, name='discover'),
]
