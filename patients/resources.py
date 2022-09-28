'''
Created on Dec 14, 2018

@author: b.dimitriadis
'''

from import_export import resources
from patients.models import BadHabit
from patients.models import Patient


class PatientResource(resources.ModelResource):
    class Meta:
        model = Patient