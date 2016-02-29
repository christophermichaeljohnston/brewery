from django.db import models

from port.models import Port

class Fermenter(models.Model):
  MODES = (
    ('C', 'CHILL'),
    ('H', 'HEAT'),
  )
  sn  = models.CharField(max_length=16)
  dev = models.CharField(max_length=12, default="")
  mode = models.CharField(max_length=1, choices=MODES, default="C")
  setpoint = models.DecimalField(max_digits=5, decimal_places=2, default=64.0)
  hysteresis = models.DecimalField(max_digits=2, decimal_places=1, default=0.1)
  pumprun = models.IntegerField(default=5000)
  pumpdelay = models.IntegerField(default=60000)

class Temperature(models.Model):
  fermenter = models.ForeignKey(Fermenter, on_delete=models.CASCADE)
  temperature = models.DecimalField(max_digits=5, decimal_places=2)
  datetime = models.DateTimeField()
