from django.conf.urls import url

from . import views

app_name = 'equipment'
urlpatterns = [
    url(r'^discover/$', views.discover, name='discover'),
    url(r'^fermenters/$', views.FermentersView.as_view(), name='fermenters'),
    url(r'^keezers/$', views.KeezersView.as_view(), name='keezers'),
    url(r'^fermenter/(?P<pk>[0-9]+)/$', views.FermenterView.as_view(), name='fermenter'),
    url(r'^fermenter/(?P<pk>[0-9]+)/edit/$', views.fermenter_edit, name='fermenter_edit'),
    url(r'^fermenter/(?P<pk>[0-9]+)/save/$', views.fermenter_save, name='fermenter_save'),
]
