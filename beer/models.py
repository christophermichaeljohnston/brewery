from django.db import models


class Beer(models.Model):
  from fermenter.models import Fermenter
  name = models.CharField(max_length=16, null=True, blank=True)
  recipe = models.TextField(null=True, blank=True)
  fermenter = models.OneToOneField(Fermenter, on_delete=False, null=True)

  def set_fermenter(self, fermenter):
    self.fermenter = fermenter
    self.save()

class Log(models.Model):
  beer = models.ForeignKey(Beer, on_delete=models.CASCADE)
  log = models.CharField(max_length=256, null=True, blank=True)
  date = models.DateTimeField(null=True)

class Temperature(models.Model):
  beer = models.ForeignKey(Beer, on_delete=models.CASCADE)
  setpoint = models.DecimalField(max_digits=5, decimal_places=2, null=True)
  temperature = models.DecimalField(max_digits=7, decimal_places=4, null=True)
  date = models.DateTimeField(null=True)
