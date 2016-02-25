from django.db import models

class Fermenter(models.Model):
  sn  = models.CharField(max_length=16)
  dev = models.CharField(max_length=12, default="")
  mode = models.CharField(max_length=12, default="CHILL")
  setpoint = models.DecimalField(max_digits=5, decimal_places=2, default=64.0)

class Keezer(models.Model):
  sn  = models.CharField(max_length=16)
  dev = models.CharField(max_length=12)
