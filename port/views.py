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
  port_initialize()
  import glob
  for port in glob.glob(PORT_PATH):
    port_open(port)
    time.sleep(3)
    sn = port_cmd(port,"getSN")
    type = port_cmd(port,"getType")
    Port.objects.create(port=port,sn=sn,type=type)
  return redirect('port:list')

def port_initialize():
  global ports
  for port in ports:
    port_close(port)
  ports = {}
  Port.objects.all().delete()

def port_open(port):
  global ports
  ports[port] = serial.Serial(port=port, baudrate=9600, timeout=1.0, write_timeout=1.0)
  time.sleep(3)

def port_close(port):
  global ports
  ports[port].close()

def port_cmd(port, cmd):
  global ports
  ports[port].reset_input_buffer()
  ports[port].reset_output_buffer()
  ports[port].write((cmd+"\n").encode())
  return ports[port].readline().decode().rstrip('\n').rstrip('\r')

def port_check(port):
  global ports
  if not port in ports:
    port_open(port)

class PortAPI:

  def cmd(sn, cmd):
    global ports
    port = Port.objects.get(sn=sn).port
    port_check(port)
    ports[port].reset_input_buffer()
    ports[port].reset_output_buffer()
    ports[port].write((cmd+"\n").encode())
    return ports[port].readline().decode().rstrip('\n').rstrip('\r')
