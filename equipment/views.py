from django.shortcuts import redirect, render
from django.views import generic

from .models import Fermenter, Keezer

def discover(request):
#  import glob
#  for file in glob.glob("/dev/ttyACM*"):
#    if not Serial.objects.filter(path=file).exists():
#      Serial.objects.create(path=file)
  return render(request, 'equipment/discover.html')

class FermentersView(generic.ListView):
  def get_queryset(self):
    return Fermenter.objects.order_by('tag')

class KeezersView(generic.ListView):
  def get_queryset(self):
    return Keezer.objects.order_by('tag')
