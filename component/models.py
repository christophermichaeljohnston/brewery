from django.db import models

from device.models import Device

class Component(models.Model):
  device = models.ForeignKey(Device, on_delete=models.CASCADE)
  sn     = models.CharField(max_length=16)
  type   = models.CharField(max_length=16)

  @classmethod
  def discover(cls, device):
    from fermenter.models import Fermenter
    sn = Device.serial_cmd(device.device, 'getSN')
    type = Device.serial_cmd(device.device, 'getType')
    try:
      c = Component.objects.get(sn=sn)
    except Component.DoesNotExist:
      c = Component.objects.create(device=device, sn=sn, type=type)
    if type == 'FERMENTER':
      Fermenter.discover(c)
