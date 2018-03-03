from django.shortcuts import redirect
from django.views import generic

from .models import Component

class ListView(generic.ListView):
  template_name = "component/list.html"
  def get_queryset(self):
    return Component.objects.order_by('device__device')
