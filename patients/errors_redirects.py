'''
Created on Nov 21, 2018

@author: b.dimitriadis
'''

from django.http import HttpResponseForbidden
from django.shortcuts import render


def forbidden_redirect(request):
    return HttpResponseForbidden(
            render(request, "patients/patient_errors.html", context={
                'window_title': "Δεν επιτρέπεται η πρόσβαση!",
#                 'title': "Μητρώο Ασθενών με χρόνια αναπνευστικά νοσήματα",
#                 'subtitle': "και χρήση αναπνευστικών συσκευών στο σπίτι",
                'exception':
                'Δεν επιτρέπεται η απευθείας πρόσβαση σε αυτήν τη σελίδα'})
            )
