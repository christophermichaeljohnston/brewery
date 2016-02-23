from django.db import models

class Type(models.Model):
  name = models.CharField(max_length=16)

class Serial(models.Model):
  path = models.CharField(max_length=12, blank=False, default=None)
  type = models.ForeignKey(Type)
  tag  = models.CharField(max_length=16, blank=True, default="")
