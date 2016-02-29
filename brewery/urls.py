from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^', include('base.urls')),
    url(r'^fermenter/', include('fermenter.urls')),
    url(r'^port/', include('port.urls')),
    url(r'^admin/', admin.site.urls),
]
