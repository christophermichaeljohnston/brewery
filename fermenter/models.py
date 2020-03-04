from django.db import models
from django.utils import timezone


from background_task import background
from background_task.models import Task

from decimal import *
from datetime import timedelta

import urllib.request

class Fermenter(models.Model):
  from component.models import Component

  MODES = (
    ('0', 'OFF'),
    ('1', 'ON'),
  )
  component = models.ForeignKey(Component, on_delete=models.CASCADE)
  name = models.CharField(max_length=16, null=True, blank=True)
  fid = models.IntegerField(null=True, blank=True)
  mode = models.CharField(max_length=1, choices=MODES, null=True, blank=True)
  setpoint = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
  hysteresis = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
  anticycle = models.IntegerField(null=True, blank=True)
  temperature = models.DecimalField(max_digits=7, decimal_places=4, null=True, blank=True)
  date = models.DateTimeField(null=True, blank=True)

  def __str__(self):
    return str(self.name)

  def get_mode(self):
    from device.models import Device
    self.mode = Device.serial_cmd(self.component.device.device,'getMode,'+str(self.fid))
    self.save()

  def set_mode(self, mode):
    from device.models import Device
    from beer.models import Log
    if self.mode != mode:
      Device.serial_cmd(self.component.device.device,'setMode,'+str(self.fid)+','+mode)
      self.get_mode()
      if hasattr(self, 'beer'):
        if mode == str(0):
          Log.objects.create(beer=self.beer, log='set mode off', date=timezone.now())
        else:
          Log.objects.create(beer=self.beer, log='set mode on', date=timezone.now())

  def get_setpoint(self):
    from device.models import Device
    self.setpoint = Device.serial_cmd(self.component.device.device,'getSetpoint,'+str(self.fid))
    self.save()

  def set_setpoint(self, setpoint):
    from device.models import Device
    from beer.models import Log
    if self.setpoint != Decimal(setpoint):
      Device.serial_cmd(self.component.device.device,'setSetpoint,'+str(self.fid)+','+setpoint)
      self.get_setpoint()
      if hasattr(self, 'beer'):
        Log.objects.create(beer=self.beer, log='set setpoint '+str(setpoint)+'F', date=timezone.now())

  def get_hysteresis(self):
    from device.models import Device
    self.hysteresis = Device.serial_cmd(self.component.device.device,'getHysteresis,'+str(self.fid))
    self.save()

  def set_hysteresis(self, hysteresis):
    from device.models import Device
    from beer.models import Log
    if self.hysteresis != Decimal(hysteresis):
      Device.serial_cmd(self.component.device.device,'setHysteresis,'+str(self.fid)+','+hysteresis)
      self.get_hysteresis()
      if hasattr(self, 'beer'):
        Log.objects.create(beer=self.beer, log='set hysteresis '+str(hysteresis), date=timezone.now())

  def get_anticycle(self):
    from device.models import Device
    self.anticycle = Device.serial_cmd(self.component.device.device,'getAntiCycle,'+str(self.fid))
    self.save()

  def set_anticycle(self, anticycle):
    from device.models import Device
    from beer.models import Log
    if self.anticycle != Decimal(anticycle):
      Device.serial_cmd(self.component.device.device,'setAntiCycle,'+str(self.fid)+','+anticycle)
      self.get_anticycle()
      if hasattr(self, 'beer'):
        Log.objects.create(beer=self.beer, log='set anticycle '+str(anticycle), date=timezone.now())

  @background()
  def probe_temperature(fermenter_id):
    f = Fermenter.objects.get(pk=fermenter_id)
    if f.component:
      urllib.request.urlopen('http://127.0.0.1:8000/fermenter/'+str(f.id)+'/get_temperature/')

  @background()
  def ramp_temperature(fermenter_id, setpoint):
    f = Fermenter.objects.get(pk=fermenter_id)
    if f.component:
      urllib.request.urlopen('http://127.0.0.1:8000/fermenter/'+str(f.id)+'/set_setpoint/?setpoint='+setpoint)

  @classmethod
  def discover(cls, component):
    for fid in range(2):
      try:
        f = cls.objects.get(component=component, fid=fid)
      except Fermenter.DoesNotExist:
        f = cls.objects.create(component=component, fid=fid)
      f.get_mode()
      f.get_setpoint();
      f.get_hysteresis();
      f.get_anticycle();
      verbose_name="probe_temperature_"+str(f.id)
      try:
        t = Task.objects.get(verbose_name=verbose_name)
      except Task.DoesNotExist:
        cls.probe_temperature(f.id, verbose_name=verbose_name, repeat=60)

  @classmethod
  def ramp(cls, fermenter, new_setpoint, step, interval):
    setpoint = fermenter.setpoint
    target = Decimal(new_setpoint)
    schedule = 0
    if target > setpoint:
      while setpoint < target:
        setpoint += Decimal(step)
        if setpoint > target:
            setpoint = target
        verbose_name="ramp_temperature_"+str(setpoint)+"_"+str(fermenter.id)
        cls.ramp_temperature(fermenter.id, str(setpoint), verbose_name=verbose_name, schedule=timedelta(minutes=schedule))
        schedule += int(interval)
    else:
      while setpoint > target:
        setpoint -= Decimal(step)
        if setpoint < target:
            setpoint = target
        verbose_name="ramp_temperature_"+str(setpoint)+"_"+str(fermenter.id)
        cls.ramp_temperature(fermenter.id, str(setpoint), verbose_name=verbose_name, schedule=timedelta(minutes=schedule))
        schedule += int(interval)
