from django.db import models

from port.models import Port

class Fermenter(models.Model):
  MODES = (
    ('0', 'OFF'),
    ('1', 'CHILL'),
    ('2', 'HEAT'),
  )
  fid = models.IntegerField()
  sn = models.CharField(max_length=16)
  name = models.CharField(max_length=16, default="")
  mode = models.CharField(max_length=1, choices=MODES, default="0")
  setpoint = models.DecimalField(max_digits=5, decimal_places=2, default=64.0)
  hysteresis = models.DecimalField(max_digits=2, decimal_places=1, default=0.1)
  rampstep = models.DecimalField(max_digits=2, decimal_places=1, default=0.0)
  ramppoint = models.DecimalField(max_digits=5, decimal_places=2, default=64.0)
  rampdelay = models.IntegerField(default=3600000)
  pumprun = models.IntegerField(default=5000)
  pumpdelay = models.IntegerField(default=60000)

class Temperature(models.Model):
  fermenter = models.ForeignKey(Fermenter, on_delete=models.CASCADE)
  temperature = models.DecimalField(max_digits=5, decimal_places=2)
  datetime = models.DateTimeField()
