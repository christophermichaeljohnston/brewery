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
      if not f.mode == int(request.POST.get("mode")):
        Device.serial_cmd(f.component.device.device,"setMode,"+request.POST.get('mode'))
        f.mode = Device.serial_cmd(f.component.device.device,'getMode')
      if not f.setpoint == Decimal(request.POST.get('setpoint')):
        Device.serial_cmd(f.component.device.device,'setSetpoint,'+request.POST.get('setpoint'))
        f.setpoint = Device.serial_cmd(f.component.device.device,'getSetpoint')
      if not f.hysteresis == Decimal(request.POST.get('hysteresis')):
        Device.serial_cmd(f.component.device.device,'setHysteresis,'+request.POST.get('hysteresis'))
        f.hysteresis = Device.serial_cmd(f.component.device.device,'getHysteresis')
      if not f.anticycle == request.POST.get('anticycle'):
        Device.serial_cmd(f.component.device.device,'setAntiCycle,'+request.POST.get('anticycle'))
        f.anticycle = Device.serial_cmd(f.component.device.device,'getAntiCycle')
      if not f.antifight == request.POST.get('antifight'):
        Device.serial_cmd(f.component.device.device,'setAntiFight,'+request.POST.get('antifight'))
        f.antifight = int(Device.serial_cmd(f.component.device.device,'getAntiFight'))
      f.save()
    return redirect('fermenter:detail', pk=f.id)
  else:
    form = FermenterForm(instance=f)
    return render(request, 'fermenter/form.html', {'form': form, 'fermenter': f})

def get_temperature(request, pk):
  from device.models import Device
  from beer.models import Temperature
  f = Fermenter.objects.get(pk=pk)
  f.internal_temperature = Device.serial_cmd(f.component.device.device, 'getInternalTemperature')
  f.external_temperature = Device.serial_cmd(f.component.device.device, 'getExternalTemperature')
  f.datetime = timezone.now()
  f.save()
  if hasattr(f, 'beer'):
    Temperature.objects.create(beer=f.beer, setpoint=f.setpoint, internal=f.internal_temperature, external=f.external_temperature, datetime=timezone.now())
  return HttpResponse("internal:" + f.internal_temperature + " external:" + f.external_temperature)

def set_setpoint(request, pk):
  from device.models import Device
  setpoint = request.GET.get('setpoint')
  f = Fermenter.objects.get(pk=pk)
  Device.serial_cmd(f.component.device.device, "setSetpoint,"+str(f.fid)+','+setpoint)
  f.setpoint = Device.serial_cmd(f.component.device.device, "getSetpoint,"+str(f.fid))
  f.save()
  return HttpResponse(f.setpoint)
