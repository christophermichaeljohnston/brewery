from django.db import models, transaction

import glob
import serial
import time

DEVICE_PATH = "/dev/ttyACM*"
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
    devices[device] = serial.Serial(port=device, baudrate=9600, timeout=1.0, write_timeout=1.0)
    time.sleep(3)
    d = Device.objects.get(device=device)
    d.connected=True
    d.save()

  def serial_close(device):
    global devices
    devices[device].close()
    d = Device.objects.get(device=device)
    d.connected=False
    d.save()

  @classmethod
  def discover(cls):
    from component.models import Component
    cls.initialize()
    Component.initialize()
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
    if device not in devices:
      cls.serial_open(device)
    with transaction.atomic():
      lock = cls.objects.select_for_update().get(device=device)
      devices[device].reset_input_buffer()
      devices[device].reset_output_buffer()
      devices[device].write((cmd+"\n").encode())
      result = devices[device].readline().decode().rstrip('\n').rstrip('\r')
      return result
