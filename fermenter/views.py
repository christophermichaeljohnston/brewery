from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.views import generic
from django.utils import timezone
from django.contrib import messages
from datetime import datetime, timedelta
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
  messages.info(request, "Discovering...")
  messages.debug(request,"hello debug")
  messages.info(request,"hello info")
  messages.success(request,"hello success")
  messages.warning(request,"hello warning")
  messages.error(request,"hello error")
  for port in Port.objects.filter(type='F'):
    try:
      f = Fermenter.objects.get(sn=port.sn)
    except Fermenter.DoesNotExist:
      f = Fermenter(sn=port.sn)
    sync(f)
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
    return render(request, 'fermenter/form.html', {'form': form, 'fermenter': f})

def sync(f):
  f.tag = PortAPI.cmd(f.sn, "getTag")
  f.mode = PortAPI.cmd(f.sn, "getMode")
  f.setpoint = PortAPI.cmd(f.sn, "getSetpoint")
  f.hysteresis = PortAPI.cmd(f.sn, "getHysteresis")
  f.pumprun = PortAPI.cmd(f.sn, "getPumpRun")
  f.pumpdelay = PortAPI.cmd(f.sn, "getPumpDelay")
  f.save()

def temperatures(request):
  for f in Fermenter.objects.all():
    t = PortAPI.cmd(f.sn, "getTemperature")
    dt = timezone.now()
    Temperature.objects.create(fermenter=f, temperature=t, datetime=dt)
  return HttpResponse("saved new temperatures")

def chart(request, pk):
  fermenter = Fermenter.objects.get(pk=pk)
  return render(request, 'fermenter/chart.html', {'fermenter': fermenter})

def chart_data(request, pk):
  now = timezone.now()
  period = request.GET.get('period')
  if period == "hour":
    threshold = now - timedelta(hours=1)
    format = '%%Y-%%m-%%d %%H:%%i:00'
    div = 60*3
  elif period == "day":
    threshold = now - timedelta(days=1)
    format = '%%Y-%%m-%%d %%H:%%i:00'
    div = 60*10
  elif period == "week":
    threshold = now - timedelta(weeks=1)
    format = '%%Y-%%m-%%d %%H:00:00'
    div = 60*60*2
  else:
    threshold = now - timedelta(days=1)
    format = '%%Y-%%m-%%d %%H:%%i:00'
  sql = "select id, date_format(datetime, '"+format+"') as nested, avg(temperature) as temperature from fermenter_temperature where fermenter_id = '"+pk+"' and datetime >= '"+threshold.strftime('%Y-%m-%d %H:%M:%S')+"' group by unix_timestamp(date_format(datetime, '"+format+"')) div "+str(div)+" order by datetime"
  response = {}
  response['start'] = [int(threshold.strftime('%s'))*1000]
  response['end'] = [int(now.strftime('%s'))*1000]
  response['data'] = []
  for t in Temperature.objects.raw(sql):
    response['data'].append([int(datetime.strptime(t.nested, '%Y-%m-%d %H:%M:%S').strftime('%s'))*1000,round(float(t.temperature),2)])
  return HttpResponse(json.dumps(response), content_type="application/json")
