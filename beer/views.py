from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.views import generic
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Avg

import json

from .models import Beer, Temperature
from .forms import BeerForm, BeerStartForm, BeerRampForm

from fermenter.models import Fermenter

from background_task.models import Task

class ListView(generic.ListView):
  template_name = 'beer/list.html'
  def get_queryset(self):
    return Beer.objects.order_by('-created')

class DetailView(generic.DetailView):
  template_name = "beer/detail.html"
  model = Beer
  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    b = Beer.objects.get(pk=self.kwargs['pk'])
    if b.fermenter:
      context['ramp'] = Task.objects.filter(verbose_name__regex=r'ramp.*_'+str(b.fermenter.id)+'$')
    return context

def create(request):
  if request.method == 'POST':
    form = BeerForm(request.POST)
    if "save" in request.POST and form.is_valid():
      b = Beer.objects.create(name=request.POST.get('name'), created=timezone.now())
      return redirect('beer:detail', b.id)
    else:
      return redirect('beer:list')
  else:
    form = BeerForm()
    return render(request, 'beer/form.html', {'form': form})

def edit(request, pk):
  b = Beer.objects.get(pk=pk)
  if request.method == 'POST':
    form = BeerForm(request.POST)
    if "save" in request.POST and form.is_valid():
      b.name = request.POST.get('name')
      b.save()
    return redirect('beer:detail', b.id)
  else:
    form = BeerForm(instance=b)
    return render(request, 'beer/form.html', {'form': form, 'beer': b})

def delete(request, pk):
  b = Beer.objects.get(pk=pk)
  b.delete()
  return redirect('beer:list')

def start(request, pk):
  b = Beer.objects.get(pk=pk)
  if request.method == 'POST':
    if "save" in request.POST:
      form = BeerStartForm(request.POST)
      if form.is_valid():
        f = Fermenter.objects.get(pk=request.POST.get('fermenter'))
        b.fermenter = f
        b.save()
        return redirect('fermenter:edit', pk=f.id)
      else:
        return redirect('beer:detail', pk=b.id)
    else:
      return redirect('beer:detail', pk=b.id)
  else:
    form = BeerStartForm(instance=b)
    return render(request, 'beer/form.html', {'form': form, 'beer': b})
  
def stop(request, pk):
  b = Beer.objects.get(pk=pk)
  Task.objects.filter(verbose_name__regex=r'ramp.*_'+str(b.fermenter.id)+'$').delete()
  f = b.fermenter
  b.fermenter = None
  b.save()
  return redirect('fermenter:edit', pk=f.id)
  #return redirect('beer:detail', pk)

def start_ramp(request, pk):
  b = Beer.objects.get(pk=pk)
  if request.method == 'POST':
    form = BeerRampForm(request.POST)
    if "save" in request.POST and form.is_valid():
      Fermenter.ramp(b.fermenter, request.POST.get('new_setpoint'), request.POST.get('step'), request.POST.get('interval'))
    return redirect('beer:detail', b.id)
  else:
    form = BeerRampForm(instance=b)
    return render(request, 'beer/form.html', {'form': form, 'beer': b})

def stop_ramp(request, pk):
  b = Beer.objects.get(pk=pk)
  Task.objects.filter(verbose_name__regex=r'ramp.*_'+str(b.fermenter.id)+'$').delete()
  return redirect('beer:detail', b.id)

def chart_data(request, pk):
  period = request.GET.get('period')
  b = Beer.objects.get(pk=pk)
  if period == 'hour':
    delta = timezone.now() - timedelta(hours=1)
    div = 60
  elif period == 'day':
    delta = timezone.now() - timedelta(days=1)
    div = 60*5
  elif period == 'week':
    delta = timezone.now() - timedelta(weeks=1)
    div = 60*30
  else:
    delta = b.temperature_set.first().datetime
    count = b.temperature_set.count()
    if count > 336:
      div = count*60/336
    else:
      div = 60

  ts = b.temperature_set.filter(datetime__gte=delta).extra(select={'timestamp':'unix_timestamp(datetime) div '+str(div)}).values('timestamp').annotate(avg_internal=Avg('internal')).annotate(avg_external=Avg('external')).annotate(avg_setpoint=Avg('setpoint')).order_by('timestamp')

  response = {}
  response['data'] = {}
  response['data']['setpoint'] = []
  response['data']['internal'] = []
  response['data']['external'] = []
  for t in ts:
    response['data']['setpoint'].append([t['timestamp']*div*1000,round(t['avg_setpoint'],1)])
    response['data']['internal'].append([t['timestamp']*div*1000,round(t['avg_internal'],1)])
    response['data']['external'].append([t['timestamp']*div*1000,round(t['avg_external'],1)])
  return HttpResponse(json.dumps(response), content_type="application/json")
