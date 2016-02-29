from __future__ import absolute_import

from celery import shared_task

from .models import Fermenter

@shared_task
def add(x,y):
  return x + y

@shared_task
def temperatures():
  foo()
  return "done"
