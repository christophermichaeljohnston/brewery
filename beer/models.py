from django.db import models

from fermenter.models import Fermenter

class Beer(models.Model):
  fermenter = models.OneToOneField(Fermenter, on_delete=False, null=True, blank=True)
  name = models.CharField(max_length=16, null=True, blank=True)
  created = models.DateTimeField(null=True, blank=True)

class Temperature(models.Model):
  beer = models.ForeignKey(Beer, on_delete=models.CASCADE)
  setpoint = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
  measured = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
  datetime = models.DateTimeField(null=True, blank=True)
