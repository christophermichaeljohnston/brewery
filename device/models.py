from django.db import models, transaction

import glob
import serial

#DEVICE_PATH = "/dev/ttyACM*"
DEVICE_PATH = '/dev/ttyS*'
devices = {}

class Device(models.Model):
  device = models.CharField(max_length=16)
  connected = models.BooleanField(default=False)

  def initialize():
    global devices
    for device in devices:
      Device.serial_close(device)
    devices = {}
    Device.objects.all().update(connected=False)

  def serial_open(device):
    global devices
    # open it
    devices[device] = 'foo'
    d = Device.objects.get(device=device)
    d.connected=True
    d.save()

  def serial_close(device):
    global devices
    #devices[device].close()
    d = Device.objects.get(device=device)
    d.connected=False
    d.save()

  @classmethod
  def discover(cls):
    from component.models import Component
    cls.initialize()
    for device in glob.glob(DEVICE_PATH):
      try:
        d = cls.objects.get(device=device)
      except cls.DoesNotExist:
        d = cls.objects.create(device=device)
      cls.serial_open(d.device)
      Component.discover(d)

  @classmethod
  def serial_cmd(cls, device, cmd):
    global devices
    import random
    with transaction.atomic():
      lock = cls.objects.select_for_update().get(device=device)
      #devices[device].reset_input_buffer()
      #devices[device].reset_output_buffer()
      #devices[device].write((cmd+"\n").encode())
      #result = devices[device].readline().decode().rstrip('\n').rstrip('\r')
      if cmd == 'getSN':
        result = device
      elif cmd == 'getType':
        result = "FERMENTER"
      elif cmd == 'getTemperature,0':
        result = 64 + (random.randint(0,10)/10)
      elif cmd == 'getTemperature,1':
        result = 64 + (random.randint(0,10)/10)
    return result
