from django import forms

from .models import Beer
from fermenter.models import Fermenter

class BeerForm(forms.ModelForm):
  class Meta:
    model = Beer
    fields = ('name',)

class BeerStartForm(forms.ModelForm):
  fermenter = forms.ModelChoiceField(queryset=Fermenter.objects.filter(beer__isnull=True).order_by('name'),required=False)
  class Meta:
    model = Beer
    fields = ('fermenter',)

class BeerRampForm(forms.ModelForm):
  new_setpoint = forms.DecimalField(max_digits=5, decimal_places=2, label='New Set Point')
  step = forms.DecimalField(max_digits=5, decimal_places=2, label='Step')
  interval = forms.DecimalField(max_digits=5, decimal_places=2, label='Interval (minutes)')
  class Meta:
    model = Beer
    fields = ('new_setpoint', 'step', 'interval')
