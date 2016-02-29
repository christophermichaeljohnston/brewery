from django.db import models

class Device(models.Model):
  device = models.CharField(max_length=16)
