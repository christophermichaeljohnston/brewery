from django.db import models

class Port(models.Model):
  TYPES = (
    ('F', 'Fermenter'),
    ('K', 'Keezer'),
  )
  port = models.CharField(max_length=16)
  type = models.CharField(max_length=1, choices=TYPES)
