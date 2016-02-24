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

class KeezersView(generic.ListView):
  def get_queryset(self):
    return Keezer.objects.order_by('sn')

def discover(request):
  log = "Initializing existing equipment...\n"
  serial_close_all()
  fermenter_remove_dev_all()
  log = "Discovering equipment...\n"
  import glob
  for file in glob.glob(DEVICE_PATH):
    log += "Found: " + file + "\n";
    if not serial_device[file].exists():
      serial_open(file)
      equipment_create_or_update(file)
  return render(request, 'equipment/discover.html', {'log': log})

def serial_open(file):
  serial_device[file] = serial.Serial(port=file, baudrate=9600)
  time.sleep(3)

def serial_close(file):
  serial_device[file].close()

def serial_close_all():
  for sd in serial_device:
    serial_close(sd)
  serial_device = {}

def serial_cmd(file, cmd):
  serial_device[file].flushInput()
  serial_device[file].flushOutput()
  serial_device[file].write(cmd.encode())
  return serial_device[file].readline().decode().rstrip('\n')

def equipment_create_or_update(file):
  type = serial_cmd(file, "getType")
  if type == "FERMENTER":
    fermenter_create_or_update(file)

def fermenter_create_or_update(file):
  sn = serial_cmd(file, "getSN")
  f = Fermenter.objects.get(sn=sn)
  if not f.exists():
    f = Fermenter(sn=sn)
    f.save()
  f.dev = file
  f.save()

def fermenter_remove_dev_all():
  Fermenter.objects.all.update(dev=None)
