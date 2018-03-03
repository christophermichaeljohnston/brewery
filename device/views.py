from django.shortcuts import redirect
from django.views import generic

from .models import Device

class ListView(generic.ListView):
  template_name = "device/list.html"
  def get_queryset(self):
    return Device.objects.order_by('device')

def discover(request):
  Device.discover()
  return redirect('device:list')
