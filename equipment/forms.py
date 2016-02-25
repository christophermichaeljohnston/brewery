from django import forms

from .models import Fermenter

class FermenterForm(forms.ModelForm):

  class Meta:
    model = Fermenter
    fields = ('sn', 'mode',)
