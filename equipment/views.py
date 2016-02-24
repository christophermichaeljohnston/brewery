from django.shortcuts import redirect, render
from django.views import generic

from .models import Fermenter, Keezer

DEVICE_PATH = "/dev/ttyACM*"

import serial
serial_device = {}

def discover(request):
  log = "Discovering equipment...\n";
  import glob
  for file in glob.glob(DEVICE_PATH):
    log += "Found: " + file + "\n";
    if not serial_device[file].exists():
      serial_open(file)
      create_or_update_equipment(file)
  return render(request, 'equipment/discover.html', {'log': log})

def serial_open(file):
  serial_device[file] = serial.Serial(port=file, baudrate=9600)

def serial_close(file):
  serial_device[file].close()

def serial_cmd(file, cmd):
  serial_device[file].flushInput()
  serial_device[file].flushOutput()
  serial_device[file].write(cmd.encode())
  return ser.readline().decode().rstrip('\n')

def create_or_update_equipment(file):
  type = serial_cmd(file, "getType")
  if type == "FERMENTER":
    if not Fermenter.objects.get(serial=file).exists():
      fermenter_create(file)
    fermenter_update(file)

def fermenter_create(file):
  Fermenter.create(serial=file, tag=serial_cmd(file, "getTag"))

def fermenter_update(file):
  f = Fermenter.objects.get(serial=file)

class FermentersView(generic.ListView):
  def get_queryset(self):
    return Fermenter.objects.order_by('tag')

class KeezersView(generic.ListView):
  def get_queryset(self):
    return Keezer.objects.order_by('tag')
