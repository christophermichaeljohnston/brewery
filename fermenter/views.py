from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.views import generic
from django.utils import timezone

from .forms import FermenterForm
from .models import Fermenter
from beer.models import Beer

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
      f.set_name(request.POST.get('name'))
      f.set_mode(request.POST.get('mode'))
      f.set_setpoint(request.POST.get('setpoint'))
      f.set_hysteresis(request.POST.get('hysteresis'))
      f.set_anticycle(request.POST.get('anticycle'))
      f.set_antifight(request.POST.get('antifight'))
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
  f.date = timezone.now()
  f.save()
  if hasattr(f, 'beer'):
    Temperature.objects.create(beer=f.beer, setpoint=f.setpoint, internal_temperature=f.internal_temperature, external_temperature=f.external_temperature, date=timezone.now())
  return HttpResponse("internal_temperature:" + f.internal_temperature + " external_temperature:" + f.external_temperature)

def set_setpoint(request, pk):
  from device.models import Device
  setpoint = request.GET.get('setpoint')
  f = Fermenter.objects.get(pk=pk)
  f.set_setpoint(setpoint)
  return HttpResponse(f.setpoint)
