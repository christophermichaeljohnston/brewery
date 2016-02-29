from django import forms

from .models import Fermenter

class Form(forms.ModelForm):

  class Meta:
    model = Fermenter
    fields = ('tag', 'mode', 'setpoint', 'hysteresis', 'pumprun', 'pumpdelay')
