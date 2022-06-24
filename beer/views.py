from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.views import generic
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Avg, Max

import json

from .models import Beer, Log, Temperature
from .forms import BeerForm, LogForm, FermenterStartForm, FermenterEditForm, RampForm

from fermenter.models import Fermenter

from decimal import Decimal
from background_task.models import Task

class ListView(generic.ListView):
  template_name = 'beer/list.html'
  def get_queryset(self):
    return Beer.objects.annotate(last_log=Max('log__date')).order_by('-last_log')

class DetailView(generic.DetailView):
  template_name = "beer/detail.html"
  model = Beer
  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    b = Beer.objects.get(pk=self.kwargs['pk'])
    if b.fermenter:
      context['ramp'] = Task.objects.filter(verbose_name__regex=r'ramp.*_'+str(b.fermenter.id)+'$')
    context['form'] = LogForm()
    return context
  def post(self, request, *args, **kwargs):
    form = LogForm(request.POST)
    if "save" in request.POST and form.is_valid():
      b = Beer.objects.get(pk=self.kwargs['pk'])
      l = Log.objects.create(beer=b, log=request.POST.get('log'), date=timezone.now())
      return redirect('beer:detail', b.id)
    else:
      return redirect('beer:detail', b.id)

def create(request):
  if request.method == 'POST':
    form = BeerForm(request.POST)
    if "save" in request.POST and form.is_valid():
      b = Beer.objects.create(name=request.POST.get('name'), recipe=request.POST.get('recipe'))
      Log.objects.create(beer=b, log='Created', date=timezone.now())
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
      b.recipe = request.POST.get('recipe')
      b.save()
    return redirect('beer:detail', b.id)
  else:
    form = BeerForm(instance=b)
    return render(request, 'beer/form.html', {'form': form})

def delete(request, pk):
  b = Beer.objects.get(pk=pk)
  b.delete()
  return redirect('beer:list')

def copy(request, pk):
  b = Beer.objects.get(pk=pk)
  new_beer = Beer.objects.create(name=b.name, recipe=b.recipe)
  Log.objects.create(beer=new_beer, log='Created', date=timezone.now())
  return redirect('beer:detail', new_beer.id)

def edit_log(request, pk, log):
  l = Log.objects.get(pk=log)
  if request.method == 'POST':
    form = LogForm(request.POST)
    if "save" in request.POST and form.is_valid():
      l.log = request.POST.get('log')
      l.save()
    return redirect('beer:detail', pk)
  else:
    form = LogForm(instance=l)
    return render(request, 'beer/form.html', {'form': form})

def delete_log(request, pk, log):
  l = Log.objects.get(pk=log)
  l.delete()
  return redirect('beer:detail', pk)

def start_fermenter(request, pk):
  b = Beer.objects.get(pk=pk)
  if request.method == 'POST':
    if "save" in request.POST:
      form = FermenterStartForm(request.POST)
      if form.is_valid():
        f = Fermenter.objects.get(pk=request.POST.get('fermenter'))
        b.set_fermenter(f)
        Log.objects.create(beer=b, log='Started', date=timezone.now())
        f.set_setpoint(request.POST.get('setpoint'))
        f.set_mode(request.POST.get("mode"))
    return redirect('beer:detail', pk=b.id)
  else:
    form = FermenterStartForm()
    return render(request, 'beer/form.html', {'form': form})

def edit_fermenter(request, pk):
  b = Beer.objects.get(pk=pk)
  if request.method == 'POST':
    if "save" in request.POST:
      form = FermenterEditForm(request.POST)
      if form.is_valid():
        b.fermenter.set_setpoint(request.POST.get('setpoint'))
        b.fermenter.set_mode(request.POST.get("mode"))
    return redirect('beer:detail', pk=b.id)
  else:
    f = Fermenter.objects.get(pk=b.fermenter.id)
    form = FermenterEditForm(instance=f)
    return render(request, 'beer/form.html', {'form': form})
  
def stop_fermenter(request, pk):
  b = Beer.objects.get(pk=pk)
  Task.objects.filter(verbose_name__regex=r'ramp.*_'+str(b.fermenter.id)+'$').delete()
  b.fermenter.set_mode(str(0))
  b.set_fermenter(None)
  Log.objects.create(beer=b, log='Stopped', date=timezone.now())
  return redirect('beer:detail', pk)

def start_ramp(request, pk):
  b = Beer.objects.get(pk=pk)
  if request.method == 'POST':
    form = RampForm(request.POST)
    if "save" in request.POST and form.is_valid():
      Fermenter.ramp(b.fermenter, request.POST.get('new_setpoint'), request.POST.get('step'), request.POST.get('interval'))
    return redirect('beer:detail', b.id)
  else:
    form = RampForm(instance=b)
    return render(request, 'beer/form.html', {'form': form})

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
    delta = b.temperature_set.first().date
    count = b.temperature_set.count()
    if count > 336:
      div = count*60/336
    else:
      div = 60

  ts = b.temperature_set.filter(date__gte=delta).extra(select={'timestamp':'unix_timestamp(date) div '+str(div)}).values('timestamp').annotate(avg_internal_temperature=Avg('internal_temperature')).annotate(avg_external_temperature=Avg('external_temperature')).annotate(avg_setpoint=Avg('setpoint')).order_by('timestamp')

  response = {}
  response['data'] = {}
  response['data']['setpoint'] = []
  response['data']['internal_temperature'] = []
  response['data']['external_temperature'] = []
  for t in ts:
    response['data']['setpoint'].append([t['timestamp']*div*1000,round(t['avg_setpoint'],1)])
    response['data']['internal_temperature'].append([t['timestamp']*div*1000,round(t['avg_internal_temperature'],1)])
    if t['avg_external_temperature']:
      response['data']['external_temperature'].append([t['timestamp']*div*1000,round(t['avg_external_temperature'],1)])
  return HttpResponse(json.dumps(response), content_type="application/json")
