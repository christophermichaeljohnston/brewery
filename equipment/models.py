from django.db import models

class Fermenter(models.Model):
  serial = models.CharField(max_length=12, blank=False, default=None)
  tag    = models.CharField(max_length=16, blank=True, default="")

class Keezer(models.Model):
  serial = models.CharField(max_length=12, blank=False, default=None)
  tag    = models.CharField(max_length=16, blank=True, default="")
