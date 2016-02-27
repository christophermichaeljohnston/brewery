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
      if not f.sn == request.POST.get("sn"):
        serial_cmd(f.dev,"setSN,"+request.POST.get("sn"))
      if not f.mode == request.POST.get("mode"):
        serial_cmd(f.dev,"setMode,"+request.POST.get("mode"))
      if not float(f.setpoint) == float(request.POST.get("setpoint")):
        serial_cmd(f.dev,"setSetpoint,"+request.POST.get("setpoint"))
      if not float(f.hysteresis) == float(request.POST.get("hysteresis")):
        serial_cmd(f.dev,"setHysteresis,"+request.POST.get("hysteresis"))
      if not f.pumprun == int(request.POST.get("pumprun")):
        serial_cmd(f.dev,"setPumpRun,"+request.POST.get("pumprun"))
      if not f.pumpdelay == int(request.POST.get("pumpdelay")):
        serial_cmd(f.dev,"setPumpDelay,"+request.POST.get("pumpdelay"))
    fermenter_sync(f)
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
  print(cmd)
  global serial_device
  serial_device[dev].flushInput()
  serial_device[dev].flushOutput()
  serial_device[dev].write((cmd+"\n").encode())
  result = serial_device[dev].readline().decode().rstrip('\n').rstrip('\r')
  print(result)
  return result

def equipment_create_or_update(dev):
  type = serial_cmd(dev, "getType")
  if type == "FERMENTER":
    fermenter_create_or_update(dev)

def fermenter_initialize():
  Fermenter.objects.all().update(dev="")

def fermenter_create_or_update(dev):
  sn = serial_cmd(dev, "getSN")
  print(">"+sn+"<")
  try:
    f = Fermenter.objects.get(sn=sn)
    print("found fermenter: >"+sn+"<")
  except Fermenter.DoesNotExist:
    f = Fermenter(sn=sn)
    print("not found fermenter: >"+sn+"<")
  f.dev = dev
  f.save()
  fermenter_sync(f)

def fermenter_sync(f):
  f.mode = serial_cmd(f.dev, "getMode")
  f.setpoint = serial_cmd(f.dev, "getSetpoint")
  f.hysteresis = serial_cmd(f.dev, "getHysteresis")
  f.pumprun = serial_cmd(f.dev, "getPumpRun")
  f.pumpdelay = serial_cmd(f.dev, "getPumpDelay")
  f.save()
