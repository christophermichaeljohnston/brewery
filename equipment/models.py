from django.db import models

class Fermenter(models.Model):
  serial_device = models.CharField(max_length=12)
