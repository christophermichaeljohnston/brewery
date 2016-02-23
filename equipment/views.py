from django.shortcuts import redirect
from django.views import generic

from .models import Type, Serial

class TypeView(generic.ListView):
  def get_queryset(self):
    return Type.objects.order_by('name')

class SerialView(generic.ListView):
  model = Serial
  def get_queryset(self):
    return Serial.objects.order_by('path')

def serial_discover(request):
  import glob
  for file in glob.glob("/dev/ttyACM*"):
    if not Serial.objects.filter(path=file).exists():
      Serial.objects.create(path=file)
  return redirect('equipment:serial')
