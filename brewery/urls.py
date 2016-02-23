from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^', include('base.urls')),
    url(r'^device/', include('device.urls')),
    url(r'^admin/', admin.site.urls),
]
