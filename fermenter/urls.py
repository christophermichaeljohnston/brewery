from django.conf.urls import url

from . import views

app_name = 'fermenter'
urlpatterns = [
    url(r'^$', views.index, name='index'),
]
