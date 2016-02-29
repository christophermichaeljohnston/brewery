from django.shortcuts import redirect, render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views import generic
from django.utils import timezone

from .models import Fermenter, Temperature
from .forms import Form

import serial
import time

DEVICE_PATH = "/dev/ttyACM*"

serial_device = {}

class ListView(generic.ListView):
  template_name = "fermenter/list.html"
  def get_queryset(self):
    return Fermenter.objects.order_by('sn')

class DetailView(generic.DetailView):
  templat_name = "fermenter/detail.html"
  model = Fermenter

def edit(request, pk):
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
    return redirect('fermenter:detail', pk=f.id)
  else:
    form = FermenterForm(instance=f)
    return render(request, 'fermenter/form.html', {'form': form})

def temperature(request, pk):
  f = Fermenter.objects.get(pk=pk)
  t = serial_cmd(f.dev, "getTemperature")
  dt = timezone.now()
  Temperature.objects.create(fermenter=f, temperature=t, datetime=dt)
  return redirect('fermenter:detail', pk=f.id)

def chart(request, pk):
  data = []
  f = Fermenter.objects.get(pk=pk)
  for ft in f.fermentertemperature_set.all():
    data.append([int(ft.datetime.strftime('%s'))*1000,float(ft.value)])
  return render(request, 'fermenter/chart.html', {'data': data})

def discover(request):
  global serial_device
  log = "Initializing existing fermenters...\n"
  serial_initialize()
  fermenter_initialize()
  log += "Discovering new and existing fermenters...\n"
  import glob
  for dev in glob.glob(DEVICE_PATH):
    log += "Found: " + dev + "\n"
    serial_open(dev)
    type = serial_cmd(dev, "getType")
    if type == "FERMENTER":
      fermenter_create_or_update(dev)
    else:
      serial_close(dev)
  return render(request, 'fermenter/discover.html', {'log': log})

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

def fermenter_initialize():
  Fermenter.objects.all().update(dev="")

def fermenter_create_or_update(dev):
  if type == "FERMENTER":
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
