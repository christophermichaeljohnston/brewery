from django.shortcuts import render
from django.views import generic

from .models import Serial

class IndexView(generic.ListView):
  template_name = 'device/index.html'
  model = Serial 
  def get_queryset(self):
    return Serial.objects.order_by('path')

def discover(request):
  import glob
  data = ""
  for file in glob.glob("/dev/ttyACM*"):
    if not Serial.objects.filter(path=file).exists():
      Serial.objects.create(path=file)
  return render(request, 'device/discover.html', {'data': data})
