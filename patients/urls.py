'''
Created on Sep 11, 2018

@author: b.dimitriadis
'''

from django.urls import path
from django.urls import re_path
from patients import views


urlpatterns = [
    path('', views.index, name='index'),
    path('pcharacteristics/<int:pat_visit_id>',
         views.patient_characteristics, name='pcharacteristics'),
    path('pventilation/<int:pat_visit_id>',
         views.patient_ventilation, name='pventilation'),
    path('pdemographics/<int:patient_id>',
         views.patient_demographics, name='pdemographics'),
    path('export_csv', views.export, name='export_csv'),
    path('pmenu/<int:patient_id>', views.patient_menu, name='pmenu'),
    path('pmenu/<int:patient_id>/<int:patient_visit_id>',
         views.patient_menu, name='pmenu'),
    path('pregistration', views.patient_registration, name='pregistration'),
    path('pregistration/<int:patient_id>',
         views.patient_registration, name='pregistration'),
    re_path(r'^pregistration/(?P<patient_code>\d{3}[A-Z]{2}\d{6})/$',
            views.patient_registration, name='pregistration'),
    path('pstate/<int:pat_visit_id>', views.patient_state, name='pstate'),
    path('pbtests/<int:pat_visit_id>',
         views.patient_breath_test, name='pbtests'),
    path('pdevtesting/<int:pat_visit_id>',
         views.patient_device_testing, name='pdevtesting'),
    path('phelpathome/<int:pat_visit_id>',
         views.patient_help_at_home, name='phelpathome'),
    path('picu/<int:pat_visit_id>',
         views.patient_icu, name='picu'),
    path('search_add', views.search_add_patient, name='search_add'),
]
