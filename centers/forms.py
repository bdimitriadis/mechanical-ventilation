'''
Created on Nov 23, 2018

@author: b.dimitriadis
'''
from django import forms

from centers.models import Center
from centers.models import Doctor


class CustomModelForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(CustomModelForm, self).__init__(*args, **kwargs)

        for field in self.fields:
            help_text = self.fields[field].help_text
            self.fields[field].help_text = None
            if help_text != '':
                self.fields[field].widget.attrs.update({
                    'class': 'has-popover',
                    'data-content': help_text,
                    'data-placement': 'right',
                    'data-container': 'body'})


class CenterForm(CustomModelForm):
    class Meta:
        model = Center
        fields = '__all__'


class DoctorForm(CustomModelForm):
    class Meta:
        model = Doctor
        fields = '__all__'
#         widgets = {
#             'centers': forms.Select,
#         }
