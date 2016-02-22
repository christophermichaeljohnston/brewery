from django.db import models

class Serial(models.Model):
  path = models.CharField(max_length=12)
