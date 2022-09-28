'''
Created on Nov 23, 2018

@author: b.dimitriadis
'''

from django.urls import path
from centers import views

urlpatterns = [
    path('center/<int:center_id>', views.center_info, name='center'),
    path('center', views.center_info, name='center'),
    path('doctor/<int:doctor_id>', views.doctor_info, name='doctor'),
    path('doctor', views.doctor_info, name='doctor'),
]
