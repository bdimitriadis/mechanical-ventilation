'''
Created on Nov 2, 2018

@author: b.dimitriadis
'''
import pytest
from patients.validators import address_validator, pat_id_validator,\
    prof_validator
from django.core.exceptions import ValidationError

class TestValidators:
    @pytest.mark.parametrize("address", [
        ("ΑΓΝΩΣΤΟΥ ΓΝΩΣΤΟΥ"),  # valid
        ("Αγνώστου Γνωστού"),  # valid
        ("Αγνώστου Γνωστού 22"),  # valid
        ("Αγνώστου Γνωστού 22, 6667"),  # valid
        ("Αγνώστου Γνωστού 22- 6667"),  # valid
        ("Αγνώστου Γνωστού, 6667"),  # valid
        ("22, 6667"),  # invalid
        ("A., 6667"),  # invalid
        ("Αγνώστου-Γνωστού 22 , 6667"),  # valid
        ("_Αγνώστου-Γνωστού 22, 6667"),  # invalid
        (" Αγνώστου-Γνωστού 22, 6667"),  # invalid
         ])
    def test_address_validator(self, address):
        with pytest.raises(ValidationError):
            address_validator(address)

    @pytest.mark.parametrize("pat_id", [
        ("333"),  # invalid
        ("3333333333"),  # invalid
        ("A333333333"),  # invalid
        ("33AA333333"),  # valid
        ("333AAAA333"),  # invalid
         ])
    def test_pat_id_validator(self, pat_id):
        with pytest.raises(ValidationError):
            pat_id_validator(pat_id)

    @pytest.mark.parametrize("profession", [
        ("dummy pr0fession"),  # invalid
        ("dummy pr.fession"),  # invalid
        ("dummy-profession"),  # invalid
        ("dummy profession"),  # valid
        ("profession"),  # invalid
         ])
    def test_prof_validator(self, profession):
        with pytest.raises(ValidationError):
            prof_validator(profession)
