'''
Created on Sep 24, 2018

@author: b.dimitriadis
'''

from django.core.validators import RegexValidator

pat_id_validator = RegexValidator(
    r"\d{3}[A-Z]{2}\d{6}",
    "Παράδειγμα ορθού αναγνωριστικού: 000MV000001")

prof_validator = RegexValidator(
    r"^[a-zA-Zα-ωΑ-Ω]+(" "[a-zA-Zα-ωΑ-Ω]+)*$",
    "Τα δεδομένα εισαγωγής σας μπορούν να περιέχουν \
     μόνο αλφαβητικούς χαρακτήρες και κενά")


address_validator = RegexValidator(
    r"^[^\W\d_ ]+([-, ]{1,3}[^\W\d_ ]+)*$",
    "Τα δεδομένα εισαγωγής σας μπορούν να περιέχουν \
     μόνο αλφαβητικούς χαρακτήρες κενά, κόμματα και παύλες")

# address_validator = RegexValidator(
#     r"^[^\W\d_ ]+([-, ]{1,3}[\w^_]+)*$",
#     "Τα δεδομένα εισαγωγής σας μπορούν να περιέχουν μόνο \
#      αλφαριθμητικούς χαρακτήρες, κενά, κόμματα και παύλες")

sn_validator = RegexValidator(
    r"^[A-Za-z\d -]*$",
    "Τα δεδομένα εισαγωγής σας μπορούν να περιέχουν μόνο \
     αλφαριθμητικούς χαρακτήρες, κενά και παύλες")
