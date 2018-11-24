from django import forms

from .models import Beer
from fermenter.models import Fermenter
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

class BeerForm(forms.ModelForm):
  helper = FormHelper()
  helper.form_class = 'form-horizontal'
  helper.label_class = 'col-sm-2'
  helper.field_class = 'col-sm-10'
  helper.add_input(Submit('save', 'Save', css_class='btn-light btn-sm'))
  helper.add_input(Submit('cancel', 'Cancel', css_class='btn-light btn-sm'))
  class Meta:
    model = Beer
    fields = ('name',)

class BeerStartForm(forms.ModelForm):
  helper = FormHelper()
  helper.form_class = 'form-horizontal'
  helper.label_class = 'col-sm-2'
  helper.field_class = 'col-sm-10'
  helper.add_input(Submit('save', 'Save', css_class='btn-light btn-sm'))
  fermenter = forms.ModelChoiceField(queryset=Fermenter.objects.filter(beer__isnull=True).order_by('name'))
  class Meta:
    model = Beer
    fields = ('fermenter',)

class BeerRampForm(forms.ModelForm):
  helper = FormHelper()
  helper.form_class = 'form-horizontal'
  helper.label_class = 'col-sm-2'
  helper.field_class = 'col-sm-10'
  helper.add_input(Submit('save', 'Save', css_class='btn-light btn-sm'))
  new_setpoint = forms.DecimalField(max_digits=5, decimal_places=2, label='New Set Point')
  step = forms.DecimalField(max_digits=5, decimal_places=2, label='Step')
  interval = forms.DecimalField(max_digits=5, decimal_places=2, label='Interval (minutes)')
  class Meta:
    model = Beer
    fields = ('new_setpoint', 'step', 'interval')
