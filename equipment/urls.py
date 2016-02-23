from django.conf.urls import url

from . import views

app_name = 'equipment'
urlpatterns = [
    url(r'^type$', views.TypeView.as_view(), name='type'),
    url(r'^serial$', views.SerialView.as_view(), name='serial'),
    url(r'^serial_discover$', views.serial_discover, name='serial_discover'),
]
