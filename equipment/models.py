from django.db import models

class Fermenter(models.Model):
  sn  = models.CharField(max_length=16, blank=False, default=None)
  dev = models.CharField(max_length=12, blank=False, default=None)

class Keezer(models.Model):
  sn  = models.CharField(max_length=16, blank=False, default=None)
  dev = models.CharField(max_length=12, blank=False, default=None)
