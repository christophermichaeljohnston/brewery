from django.shortcuts import redirect, render
from django.views import generic

from .models import Fermenter, Keezer

import time
import serial

DEVICE_PATH = "/dev/ttyACM*"

serial_device = {}

class FermentersView(generic.ListView):
  def get_queryset(self):
    return Fermenter.objects.order_by('sn')

def fermenter(request):
  return render(request, 'equipment/fermenter.html')

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
  Fermenter.objects.all().update(dev=None)

def fermenter_create_or_update(dev):
  sn = serial_cmd(dev, "getSN")
  try:
    f = Fermenter.objects.get(sn=sn)
  except Fermenter.DoesNotExist:
    f = Fermenter(sn=sn)
  f.dev = dev
  f.save()
