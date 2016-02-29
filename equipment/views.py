from django.shortcuts import redirect, render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views import generic
from django.utils import timezone

from .models import Fermenter, FermenterTemperature, Keezer
from .forms import FermenterForm

import serial
import time

DEVICE_PATH = "/dev/ttyACM*"

serial_device = {}

def init():
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
  print(log)

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

def fermenter_temperature(request, pk):
  f = Fermenter.objects.get(pk=pk)
  t = serial_cmd(f.dev, "getTemperature")
  dt = timezone.now()
  print(f.sn+" "+t)
  FermenterTemperature.objects.create(fermenter=f, value=t, datetime=dt)
  return redirect('equipment:fermenter', pk=f.id)

def fermenter_chart(request, pk):
  foo = []
  data = []
  f = Fermenter.objects.get(pk=pk)
  for ft in f.fermentertemperature_set.all():
    foo.append(ft.datetime)
    data.append([int(ft.datetime.strftime('%s'))*1000,float(ft.value)])
  return render(request, 'equipment/fermenter_chart.html', {'data': data, 'foo': foo})

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
  fermenter_sync(f)


def fermenter_sync(f):
  f.mode = serial_cmd(f.dev, "getMode")
  f.setpoint = serial_cmd(f.dev, "getSetpoint")
  f.hysteresis = serial_cmd(f.dev, "getHysteresis")
  f.pumprun = serial_cmd(f.dev, "getPumpRun")
  f.pumpdelay = serial_cmd(f.dev, "getPumpDelay")
  f.save()
