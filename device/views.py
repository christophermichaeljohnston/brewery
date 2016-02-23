from django.shortcuts import render, redirect
from django.views import generic

from .models import Serial

import serial
ser = {}

class IndexView(generic.ListView):
  template_name = 'device/index.html'
  model = Serial 
  def get_queryset(self):
    return Serial.objects.order_by('path')

def discover(request):
  import glob
  for file in glob.glob("/dev/ttyACM*"):
    if not Serial.objects.filter(path=file).exists():
      Serial.objects.create(path=file)
  return redirect('device:index')
