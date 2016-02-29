from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.views import generic
from django.utils import timezone
import json

from .models import Fermenter, Temperature
from .forms import Form

from port.models import Port
from port.views import PortAPI

class ListView(generic.ListView):
  template_name = "fermenter/list.html"
  def get_queryset(self):
    return Fermenter.objects.order_by('sn')

class DetailView(generic.DetailView):
  template_name = "fermenter/detail.html"
  model = Fermenter

def discover(request):
  for port in Port.objects.filter(type='F'):
    print(port.sn)
    try:
      f = Fermenter.objects.get(sn=port.sn)
    except Fermenter.DoesNotExist:
      f = Fermenter(sn=port.sn)
      print("not found")
    f.sync()
  return redirect('fermenter:list')

def edit(request, pk):
  f = Fermenter.objects.get(pk=pk)
  if request.method == "POST":
    form = Form(request.POST)
    if form.is_valid():
      if not f.tag == request.POST.get("tag"):
        PortAPI.cmd(f.sn,"setTag,"+request.POST.get("tag"))
      if not f.mode == request.POST.get("mode"):
        PortAPI.cmd(f.sn,"setMode,"+request.POST.get("mode"))
      if not float(f.setpoint) == float(request.POST.get("setpoint")):
        PortAPI.cmd(f.sn,"setSetpoint,"+request.POST.get("setpoint"))
      if not float(f.hysteresis) == float(request.POST.get("hysteresis")):
        PortAPI.cmd(f.sn,"setHysteresis,"+request.POST.get("hysteresis"))
      if not f.pumprun == int(request.POST.get("pumprun")):
        PortAPI.cmd(f.sn,"setPumpRun,"+request.POST.get("pumprun"))
      if not f.pumpdelay == int(request.POST.get("pumpdelay")):
        PortAPI.cmd(f.sn,"setPumpDelay,"+request.POST.get("pumpdelay"))
    sync(f)
    return redirect('fermenter:detail', pk=f.id)
  else:
    form = Form(instance=f)
    return render(request, 'fermenter/form.html', {'form': form})

def temperature(request, pk):
  f = Fermenter.objects.get(pk=pk)
  t = PortAPI.cmd(f.sn, "getTemperature")
  dt = timezone.now()
  Temperature.objects.create(fermenter=f, temperature=t, datetime=dt)
  return redirect('fermenter:detail', pk=f.id)

def chart(request, pk):
  response = {}
  response['data'] = []
  f = Fermenter.objects.get(pk=pk)
  for t in f.temperature_set.all():
    response['data'].append([int(t.datetime.strftime('%s'))*1000,float(t.temperature)])
  return HttpResponse(json.dumps(response), content_type="application/json")

def sync(f):
  f.tag = PortAPI.cmd(f.sn, "getTag")
  f.mode = PortAPI.cmd(f.sn, "getMode")
  f.setpoint = PortAPI.cmd(f.sn, "getSetpoint")
  f.hysteresis = PortAPI.cmd(f.sn, "getHysteresis")
  f.pumprun = PortAPI.cmd(f.sn, "getPumpRun")
  f.pumpdelay = PortAPI.cmd(f.sn, "getPumpDelay")
  f.save()
