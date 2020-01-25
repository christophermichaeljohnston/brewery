from django.db import models
from django.utils import timezone

from device.models import Device
from component.models import Component

from background_task import background
from background_task.models import Task

from decimal import *
from datetime import timedelta

import urllib.request

class Fermenter(models.Model):
  MODES = (
    ('0', 'OFF'),
    ('1', 'ON'),
  )
  component = models.ForeignKey(Component, on_delete=models.CASCADE)
  name = models.CharField(max_length=16, null=True, blank=True)
  mode = models.CharField(max_length=1, choices=MODES, null=True, blank=True)
  setpoint = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
  hysteresis = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
  anticycle = models.IntegerField(null=True, blank=True)
  antifight = models.IntegerField(null=True, blank=True)
  internal_temperature = models.DecimalField(max_digits=7, decimal_places=4, null=True, blank=True)
  external_temperature = models.DecimalField(max_digits=7, decimal_places=4, null=True, blank=True)
  datetime = models.DateTimeField(null=True, blank=True)

  def __str__(self):
    return str(self.name)

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
    try:
      f = cls.objects.get(component=component)
    except Fermenter.DoesNotExist:
      f = cls.objects.create(component=component)
    f.mode = Device.serial_cmd(f.component.device.device,'getMode')
    f.setpoint = Device.serial_cmd(f.component.device.device,'getSetpoint')
    f.hysteresis = Device.serial_cmd(f.component.device.device,'getHysteresis')
    f.anticycle = Device.serial_cmd(f.component.device.device,'getAntiCycle')
    f.antifight = Device.serial_cmd(f.component.device.device,'getAntiFight')
    f.save()
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
