from django.shortcuts import redirect, render
from django.views import generic

from .models import Fermenter, Keezer

import time
import serial

DEVICE_PATH = "/dev/ttyACM*"

serial_device = {}

class FermentersView(generic.ListView):
  def get_queryset(self):
    return Fermenter.objects.order_by('tag')

class KeezersView(generic.ListView):
  def get_queryset(self):
    return Keezer.objects.order_by('tag')

def discover(request):
  log = "Discovering equipment...\n";
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
  f = Fermenter.objects.get(serial=file)
  if not f.exists():
    f = Fermenter(serial=file, tag=serial_cmd(file, "getTag"))
    f.save()

