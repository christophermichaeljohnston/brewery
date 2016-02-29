from django.shortcuts import redirect
from django.views import generic

from .models import Port

import serial
import time

PORT_PATH = "/dev/ttyACM*"

ports = {}

class ListView(generic.ListView):
  template_name = "port/list.html"
  def get_queryset(self):
    return Port.objects.order_by('port')

class DetailView(generic.DetailView):
  template_name = "port/detail.html"
  model = Port

def discover(request):
  initialize()
  import glob
  for port in glob.glob(PORT_PATH):
    open(port)
    sn = cmd(port,"getSN")
    type = cmd(port,"getType")
    Port.objects.create(port=port,sn=sn,type=type)
  time.sleep(3)
  return redirect('port:list')

def initialize():
  global ports
  for port in ports:
    close(port)
  ports = {}
  Port.objects.all().delete()

def open(port):
  global ports
  ports[port] = serial.Serial(port=port, baudrate=9600, timeout=1.0, write_timeout=1.0)

def close(port):
  global ports
  ports[port].close()

def cmd(port):
  global ports
  ports[port].reset_input_buffer()
  ports[port].reset_output_buffer()
  ports[port].write((cmd+"\n").encode())
  return ports[port].readline().decode().rstrip('\n').rstrip('\r')

class PortAPI:

  def cmd(sn, cmd):
    global ports
    port = Port.objects.get(sn=sn,type=type).port
    ports[port].reset_input_buffer()
    ports[port].reset_output_buffer()
    ports[port].write((cmd+"\n").encode())
    return ports[port].readline().decode().rstrip('\n').rstrip('\r')
