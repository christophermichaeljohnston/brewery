from django.shortcuts import redirect, render
from django.views import generic

from .models import Fermenter, Keezer

def discover(request):
  log = "";
  import glob
  for file in glob.glob("/dev/ttyACM*"):
    log += file + "\n";
#    if not Serial.objects.filter(path=file).exists():
#      Serial.objects.create(path=file)
  return render(request, 'equipment/discover.html', {'log': log})

class FermentersView(generic.ListView):
  def get_queryset(self):
    return Fermenter.objects.order_by('tag')

class KeezersView(generic.ListView):
  def get_queryset(self):
    return Keezer.objects.order_by('tag')
