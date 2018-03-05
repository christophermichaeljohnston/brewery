from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.views import generic
from django.utils import timezone

from background_task.models import Task

from .forms import FermenterForm

from .models import Fermenter


class ListView(generic.ListView):
  template_name = "fermenter/list.html"
  def get_queryset(self):
    return Fermenter.objects.order_by('component__device__device')

class DetailView(generic.DetailView):
  template_name = "fermenter/detail.html"
  model = Fermenter
  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['tasks'] = Task.objects.filter(verbose_name__regex=r'_'+str(self.kwargs['pk'])+'$').order_by('run_at')
    return context

def edit(request, pk):
  f = Fermenter.objects.get(pk=pk)
  if request.method == "POST":
    form = FermenterForm(request.POST)
    if form.is_valid():
      if not f.name == request.POST.get("name"):
        f.name = request.POST.get("name")
        f.save()
        #PortAPI.cmd(f.sn,"setName,"+str(f.fid)+","+request.POST.get("name"))
    return redirect('fermenter:detail', pk=f.id)
  else:
    form = FermenterForm(instance=f)
    return render(request, 'fermenter/form.html', {'form': form, 'fermenter': f})

def get_temperature(requuest, pk):
  from device.models import Device
  from beer.models import Temperature
  f = Fermenter.objects.get(pk=pk)
  f.temperature = Device.serial_cmd(f.component.device.device, "getTemperature,"+str(f.fid))
  f.datetime = timezone.now()
  f.save()
  if hasattr(f, 'beer'):
    Temperature.objects.create(beer=f.beer, setpoint=f.setpoint, measured=f.temperature, datetime=timezone.now())
  return HttpResponse(f.temperature)
