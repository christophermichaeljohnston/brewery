from django import forms

from .models import Fermenter
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

class FermenterForm(forms.ModelForm):

  helper = FormHelper()
  helper.form_class = 'form-horizontal'
  helper.label_class = 'col-sm-2'
  helper.field_class = 'col-sm-10'
  helper.add_input(Submit('save', 'Save', css_class='btn-light btn-sm'))
  helper.add_input(Submit('cancel', 'Cancel', css_class='btn-light btn-sm'))

  class Meta:
    model = Fermenter
    fields = ('name', 'mode', 'setpoint')
