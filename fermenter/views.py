from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.views import generic
from django.utils import timezone

from .forms import FermenterForm
from .models import Fermenter

from decimal import Decimal
from background_task.models import Task

class ListView(generic.ListView):
  template_name = "fermenter/list.html"
  def get_queryset(self):
    return Fermenter.objects.order_by('name')

class DetailView(generic.DetailView):
  template_name = "fermenter/detail.html"
  model = Fermenter
  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['tasks'] = Task.objects.filter(verbose_name__regex=r'_'+str(self.kwargs['pk'])+'$').order_by('run_at')
    return context

def edit(request, pk):
  from device.models import Device
  f = Fermenter.objects.get(pk=pk)
  if request.method == "POST":
    form = FermenterForm(request.POST)
    if "save" in request.POST and form.is_valid():
      if not f.name == request.POST.get("name"):
        f.name = request.POST.get("name")
      if not f.setpoint == Decimal(request.POST.get("setpoint")):
        Device.serial_cmd(f.component.device.device,"setSetpoint,"+str(f.fid)+","+request.POST.get("setpoint"))
        f.setpoint = Device.serial_cmd(f.component.device.device,"getSetpoint,"+str(f.fid))
      if not f.mode == request.POST.get("mode"):
        Device.serial_cmd(f.component.device.device,"setMode,"+str(f.fid)+","+request.POST.get("mode"))
        f.mode = Device.serial_cmd(f.component.device.device,"getMode,"+str(f.fid))
      f.save()
    return redirect('fermenter:detail', pk=f.id)
  else:
    form = FermenterForm(instance=f)
    return render(request, 'fermenter/form.html', {'form': form, 'fermenter': f})

def get_temperature(request, pk):
  from device.models import Device
  from beer.models import Temperature
  f = Fermenter.objects.get(pk=pk)
  f.temperature = Device.serial_cmd(f.component.device.device, "getTemperature,"+str(f.fid))
  f.datetime = timezone.now()
  f.save()
  if hasattr(f, 'beer'):
    Temperature.objects.create(beer=f.beer, setpoint=f.setpoint, measured=f.temperature, datetime=timezone.now())
  return HttpResponse(f.temperature)

def set_setpoint(request, pk):
  from device.models import Device
  setpoint = request.GET.get('setpoint')
  f = Fermenter.objects.get(pk=pk)
  Device.serial_cmd(f.component.device.device, "setSetpoint,"+str(f.fid)+','+setpoint)
  f.setpoint = Device.serial_cmd(f.component.device.device, "getSetpoint,"+str(f.fid))
  f.save()
  return HttpResponse(f.setpoint)
