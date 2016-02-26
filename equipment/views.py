from django.shortcuts import redirect, render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views import generic

from .models import Fermenter, Keezer
from .forms import FermenterForm

import time
import serial

DEVICE_PATH = "/dev/ttyACM*"

serial_device = {}

class FermentersView(generic.ListView):
  def get_queryset(self):
    return Fermenter.objects.order_by('sn')

class FermenterView(generic.DetailView):
  model = Fermenter

def fermenter_edit(request, pk):
  f = Fermenter.objects.get(pk=pk)
  if request.method == "POST":
    form = FermenterForm(request.POST)
    if form.is_valid():
      print(request.POST.get("sn"))
      print(request.POST.get("mode"))
      print(request.POST.get("setpoint"))
      print(request.POST.get("hysteresis"))
      print(request.POST.get("pumprun"))
      print(request.POST.get("pumprun"))
    return redirect('equipment:fermenter', pk=f.id)
  else:
    form = FermenterForm(instance=f)
    return render(request, 'equipment/fermenter_form.html', {'form': form})

class KeezersView(generic.ListView):
  def get_queryset(self):
    return Keezer.objects.order_by('sn')

def discover(request):
  global serial_device
  log = "Initializing existing equipment...\n"
  serial_initialize()
  fermenter_initialize()
  log += "Discovering new and existing equipment...\n"
  import glob
  for dev in glob.glob(DEVICE_PATH):
    log += "Found: " + dev + "\n"
    serial_open(dev)
    equipment_create_or_update(dev)
  return render(request, 'equipment/discover.html', {'log': log})

def serial_initialize():
  global serial_device
  for dev in serial_device:
    serial_close(dev)
  serial_device = {}

def serial_open(dev):
  global serial_device
  serial_device[dev] = serial.Serial(port=dev, baudrate=9600)
  time.sleep(3)

def serial_close(dev):
  global serial_device
  serial_device[dev].close()

def serial_cmd(dev, cmd):
  global serial_device
  serial_device[dev].flushInput()
  serial_device[dev].flushOutput()
  serial_device[dev].write((cmd+"\n").encode())
  result = serial_device[dev].readline().decode().rstrip('\n').rstrip('\r')
  return result

def equipment_create_or_update(dev):
  type = serial_cmd(dev, "getType")
  if type == "FERMENTER":
    fermenter_create_or_update(dev)

def fermenter_initialize():
  Fermenter.objects.all().update(dev="")

def fermenter_create_or_update(dev):
  sn = serial_cmd(dev, "getSN")
  try:
    f = Fermenter.objects.get(sn=sn)
  except Fermenter.DoesNotExist:
    f = Fermenter(sn=sn)
  f.dev = dev
  f.save()
