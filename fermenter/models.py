from django.db import models
from django.utils import timezone

from device.models import Device
from component.models import Component

from background_task import background
from background_task.models import Task

class Fermenter(models.Model):
  MODES = (
    ('0', 'OFF'),
    ('1', 'CHILL'),
    ('2', 'HEAT'),
  )
  component = models.ForeignKey(Component, on_delete=models.CASCADE)
  fid = models.IntegerField()
  name = models.CharField(max_length=16, null=True, blank=True)
  mode = models.CharField(max_length=1, choices=MODES, null=True, blank=True)
  setpoint = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
  hysteresis = models.DecimalField(max_digits=2, decimal_places=1, null=True, blank=True)
  pumprun = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
  pumpdelay = models.IntegerField(null=True, blank=True)
  temperature = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
  datetime = models.DateTimeField(null=True, blank=True)

  @background()
  def probe_temperature(fermenter_id):
    f = Fermenter.objects.get(pk=fermenter_id)
    f.temperature = Device.serial_cmd(f.component.device.device, "getTemperature,"+str(f.fid))
    f.datetime = timezone.now()
    f.save()

  @classmethod
  def discover(cls, component):
    for fid in [0,1]:
      try:
        f = cls.objects.get(component=component, fid=fid)
      except Fermenter.DoesNotExist:
        f = cls.objects.create(component=component, fid=fid)
      verbose_name="probe_temperature_"+str(f.id)
      try:
        t = Task.objects.get(verbose_name=verbose_name)
      except Task.DoesNotExist:
        cls.probe_temperature(f.id, verbose_name=verbose_name, repeat=60)
