from django.db import models

class Sensor(models.Model):
  deviceaddress = models.CharField(max_length=16)

class Temperature(models.Model):
  sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE)
  value = models.DecimalField(max_digits=5, decimal_places=2)
  datetime = models.DateTimeField()
