from django.shortcuts import redirect, render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views import generic
from django.utils import timezone

from .models import Fermenter, Temperature
from .forms import Form

from port.views import PortAPI

class ListView(generic.ListView):
  template_name = "fermenter/list.html"
  def get_queryset(self):
    return Fermenter.objects.order_by('sn')

class DetailView(generic.DetailView):
  template_name = "fermenter/detail.html"
  model = Fermenter

def edit(request, pk):
  f = Fermenter.objects.get(pk=pk)
  if request.method == "POST":
    form = Form(request.POST)
    if form.is_valid():
      if not f.sn == request.POST.get("sn"):
        SerialAPI.cmd(f.dev,"setSN,"+request.POST.get("sn"))
      if not f.mode == request.POST.get("mode"):
        SerialAPI.cmd(f.dev,"setMode,"+request.POST.get("mode"))
      if not float(f.setpoint) == float(request.POST.get("setpoint")):
        SerialAPI.cmd(f.dev,"setSetpoint,"+request.POST.get("setpoint"))
      if not float(f.hysteresis) == float(request.POST.get("hysteresis")):
        SerialAPI.cmd(f.dev,"setHysteresis,"+request.POST.get("hysteresis"))
      if not f.pumprun == int(request.POST.get("pumprun")):
        SerialAPI.cmd(f.dev,"setPumpRun,"+request.POST.get("pumprun"))
      if not f.pumpdelay == int(request.POST.get("pumpdelay")):
        SerialAPI.cmd(f.dev,"setPumpDelay,"+request.POST.get("pumpdelay"))
    fermenter_sync(f)
    return redirect('fermenter:detail', pk=f.id)
  else:
    form = Form(instance=f)
    return render(request, 'fermenter/form.html', {'form': form})

def temperature(request, pk):
  f = Fermenter.objects.get(pk=pk)
  t = SerialAPI.cmd(f.dev, "getTemperature")
  dt = timezone.now()
  Temperature.objects.create(fermenter=f, temperature=t, datetime=dt)
  return redirect('fermenter:detail', pk=f.id)

def chart(request, pk):
  data = []
  f = Fermenter.objects.get(pk=pk)
  for ft in f.fermentertemperature_set.all():
    data.append([int(ft.datetime.strftime('%s'))*1000,float(ft.value)])
  return render(request, 'fermenter/chart.html', {'data': data})

def fermenter_initialize():
  Fermenter.objects.all().update(dev="")

def fermenter_create_or_update(dev):
  if type == "FERMENTER":
    sn = SerialAPI.cmd(dev, "getSN")
    try:
      f = Fermenter.objects.get(sn=sn)
    except Fermenter.DoesNotExist:
      f = Fermenter(sn=sn)
    f.dev = dev
    fermenter_sync(f)

def fermenter_sync(f):
  f.mode = SerialAPI.cmd(f.dev, "getMode")
  f.setpoint = SerialAPI.cmd(f.dev, "getSetpoint")
  f.hysteresis = SerialAPI.cmd(f.dev, "getHysteresis")
  f.pumprun = SerialAPI.cmd(f.dev, "getPumpRun")
  f.pumpdelay = SerialAPI.cmd(f.dev, "getPumpDelay")
  f.save()
