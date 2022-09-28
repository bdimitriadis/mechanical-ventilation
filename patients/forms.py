'''
Created on Sep 14, 2018

@author: b.dimitriadis
'''

import datetime

from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.utils.safestring import mark_safe

from centers.models import Center
from patients.exports import ExportTool
from patients.models import BadHabit
from patients.models import BreathAndSleepTest
from patients.models import Caregiver
from patients.models import DeathCause
from patients.models import DeviceTestingInfo
from patients.models import ExtraAccompanyingDisease
from patients.models import ExtraMyopathy
from patients.models import Gender
from patients.models import HelpAtHome
from patients.models import ICU
from patients.models import PatientCharacteristics
from patients.models import Patient
from patients.models import PatientState
from patients.models import PatientVentilation
from patients.models import PatientVisit

from patients.validators import pat_id_validator


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


class CaregiverForm(CustomModelForm):
    class Meta:
        model = Caregiver
        fields = ['profession',
                  'education',
                  'relation_to_patient']
        labels = {
            'profession': 'Επάγγελμα φροντιστή:',
            'education': 'Μόρφωση φροντιστή:',
            'relation_to_patient': 'Σχέση φροντιστή με τον ασθενή:',
        }

        widgets = {
            'relation_to_patient': forms.RadioSelect(
                attrs={
                    'class': 'list-inline',
                }
            )
        }

    def __init__(self, *args, **kwargs):
        super(CaregiverForm, self).__init__(*args, **kwargs)
        self.instance = kwargs.pop('instance', None)

        # If instance (caregiver) is none, delete all fields from form
        if not self.instance:
            del self.fields['profession']
            del self.fields['education']
            del self.fields['relation_to_patient']


class DemographicsForm(CustomModelForm):
    class Meta:
        model = Patient
        fields = ['residence',
                  'profession',
                  'education',
                  'comment']

        labels = {
            'residence': 'Κατοικία: ',
            'profession': 'Επάγγελμα: ',
            'education': 'Μόρφωση: ',
            'comment': 'Σχόλιο: ',
        }
        widgets = {

            'comment': forms.Textarea(attrs={'rows': 4, 'cols': 40}),
        }

    def __init__(self, *args, **kwargs):
        super(DemographicsForm, self).__init__(*args, **kwargs)
 
        self.pat = kwargs.pop('instance', None)
 
        if self.pat and not self.pat.adult:
            del self.fields['profession']
            del self.fields['education']


class VisitForm(CustomModelForm):
    class Meta:
        model = PatientVisit
        fields = ['visit_date']

        labels = {
            'visit_date': '',
        }

    def __init__(self, *args, **kwargs):
        super(VisitForm, self).__init__(*args, **kwargs)
        self.instance = kwargs.pop('instance', None)
        min_date_limit = (PatientVisit.objects.filter(
            pat_id=self.instance.pat_id).earliest(
                'visit_date').visit_date - datetime.date.today())

        self.fields['visit_date'].widget = forms.DateInput(attrs={
               'min': "{}d".format(min_date_limit.days),
               'max': '+0d',
               'placeholder': 'Επιλέξτε ημερομηνία',
               'class': 'datepicker',
        },)


class RegisterForm(CustomModelForm):

    class Meta:
        model = Patient
        fields = ['pat_id',
                  'adult',
                  'pat_condition',
                  'care_center',
                  'icu',
                  'gender',
                  'birth_year',
                  'ma_subscription_date']

        labels = {
            'pat_id': 'Αναγνωριστικό Ατόμου: ',
            'adult': 'Ηλικιακή Κατηγορία: ',
            'pat_condition': 'Κατάσταση Ασθενούς: ',
            'gender': 'Φύλο: ',
            'birth_year': 'Έτος Γεννήσεως: ',
            'ma_subscription_date': 'Ημερομηνία Εγγραφής Ασθενούς: ',
        }
        widgets = {
            'adult': forms.RadioSelect(attrs={
                'class': 'list-inline',
            },),


            'ma_subscription_date': forms.DateInput(attrs={
               'min': '-150y',
               'max': '+0d',
               'placeholder': 'Επιλέξτε ημερομηνία',
               'class': 'datepicker',
            },)
        }

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.instance = kwargs.pop('instance', None)
        self.fields['pat_id'].widget.attrs['readonly'] = True

    def is_valid(self):
        """ Overriding-extending is_valid module
        """
        super(RegisterForm, self).is_valid()

        # Extend registration validation,
        # ma_subscription_date cannot be greater than birth_date
        if self.cleaned_data.get('ma_subscription_date') and 'birth_year'\
                in self.cleaned_data and\
            self.cleaned_data.get('ma_subscription_date').year <\
                self.cleaned_data.get('birth_year'):
            self.add_error('ma_subscription_date', "Η ημερομηνία εγγραφής του ασθενούς,\
            δεν μπορεί να είναι προγενέστερη του έτους γεννήσεώς του")

        if 'birth_year' in self.cleaned_data and \
                (datetime.datetime.now().year - self.cleaned_data.get('birth_year') < 18) ==\
                self.cleaned_data.get('adult'):
            self.add_error(None,
                           "Η ηλικιακή κατηγορία του ασθενούς, πρέπει να συμβαδίζει με το έτος γεννήσεώς του")

        return not self._errors

    def save(self, commit=True):
        """ Overriding-extending save module
        """
        tmp_pat = super(RegisterForm, self).save(commit)
        if tmp_pat:
            initial_care_center = self.instance.pat_id[:3]
            filtered_centers = Center.objects.filter(code=initial_care_center)
            if filtered_centers:
                tmp_pat.care_centers.add(filtered_centers[0])

            tmp_pat.care_centers.add(self.cleaned_data.get('care_center'))
            tmp_pat.save()


class StateForm(CustomModelForm):
    total_hospitalizations = forms.IntegerField(
        label=mark_safe("Σύνολο νοσηλειών: "),
        help_text="Συνολικός αριθμός νοσηλειών ασθενούς μέχρι σήμερα"
        )

    class Meta:
        model = PatientState
        fields = ['pat_status',
                  'date_of_death',
                  'cause_of_death',
                  'hospitalizations', ]

        widgets = {
            'date_of_death': forms.DateInput(attrs={
               'min': '-150y',
               'max': '+0d',
               'placeholder': 'Επιλέξτε ημερομηνία',
               'class': 'datepicker',
            },),
        }

    def __init__(self, *args, **kwargs):
        super(StateForm, self).__init__(*args, **kwargs)
        self.instance = kwargs.pop('instance', None)
        self.fields['total_hospitalizations'].widget.attrs['readonly'] = True

        self.fields['total_hospitalizations'].initial = PatientState.objects\
            .filter(visit_id__pat_id=self.instance.visit.pat_id).aggregate(
                Sum('hospitalizations')).get(
                    'hospitalizations__sum') or 0

        # Get previous visits (in reverse order so that more recent is first)
        previous_visits = PatientVisit.objects.filter(
            pat_id=self.instance.visit.pat_id,
            visit_date__lt=self.instance.visit.visit_date)\
            .order_by('-visit_date')

        if previous_visits:
            # Initialize hospitalizations to last_visit's value
            try:
                self.instance.hospitalizations =\
                    PatientState.objects.get(
                        visit=previous_visits.first()).\
                    hospitalizations
            # If previous patient-state has not be filled in, leave it -1
            except PatientState.DoesNotExist:
                pass

    def clean(self):
        super(StateForm, self).clean()
        data = self.cleaned_data
        # If pat_status is not death, cause and date of death should be null (none)
        if 'pat_status' in self.cleaned_data and \
        self.cleaned_data.get('pat_status').pat_status != "ΘΑΝΑΤΟΣ":
            data['date_of_death'] = None
            data['cause_of_death'] = None
        return data

    def is_valid(self):
        super(StateForm, self).is_valid()

        #  Allow date_of_death field to be empty if death state is not selected
        if 'pat_status' in self.cleaned_data and\
                self.cleaned_data.get('pat_status').pat_status != "ΘΑΝΑΤΟΣ":
            if 'date_of_death' in self._errors:
                del self._errors['date_of_death']
            if 'cause_of_death' in self._errors:
                del self._errors['cause_of_death']

        elif self.instance:
            cur_visit_date = self.instance.visit.visit_date
            patient = self.instance.visit.pat_id
            if (PatientVisit.objects.filter(pat_id=patient,
                                            visit_date__gt=cur_visit_date)):
                self.add_error(
                    'pat_status',
                    "Δεν μπορεί να πραγματοποιηθεί μεταβολή της έκβασης του \
                    ασθενούς στην τιμή 'Θάνατος', ενώ υπάρχουν μεταγενέστερες \
                    της παρούσας επισκέψεις.")
            else:
                date_of_death = self.cleaned_data.get('date_of_death')
                if date_of_death and cur_visit_date < date_of_death:
                    self.add_error(
                        'date_of_death',
                        "Η ημερομηνία θανάτου του ασθενούς, δεν μπορεί να είναι\
                    μεταγενέστερη της παρούσας επίσκεψης.")

        return not self._errors


class CharacteristicsForm(CustomModelForm):
    bmi = forms.FloatField(
        label=mark_safe('BMI (kg/m<sup>2</sup>): '),
        help_text="Ο υπολογισμός αυτού του πεδίου γίνεται αυτόματα")

    class Meta:
        model = PatientCharacteristics
        exclude = ['visit']
        widgets = {
            'other_accomp': forms.CheckboxSelectMultiple,
            }

    def __init__(self, *args, **kwargs):
        super(CharacteristicsForm, self).__init__(*args, **kwargs)
        self.instance = kwargs.pop('instance', None)
        self.fields['bmi'].widget.attrs['readonly'] = True

        gen_chars = ['weight', 'height', 'bmi', 'smoker', 'alcohol',
                     'underlying_disease']

        self.underlying_dis = [
            'xap', 'other_obstructive', 'obesity_subvent',
            'sayy', 'dmd', 'myasthenia', 'nkn',
            'parkinson', 'heart_failure', 'other_neurological',
            'diaphragm_malfunction', 'posttb', 'kyphoscoliosis',
            'other_limit_lung', 'extra_myopathy']

        accomp_dis = ['cardiopathies', 'sd', 'aee', 'ay',
                      'pulmonary_hypertension', 'other_accomp']
        additional_info = ['nutrition', 'physical_activity']

        # If patient is an adult, change extra_myopathy's widget to
        # checkbox and value just to "ΑΛΛΟ". Remove smoker and alcohol fields
        if self.instance.visit.pat_id.adult:
            self.fields['extra_myopathy'].widget = forms.CheckboxInput()
            self.fields['extra_myopathy'].initial = bool(
                self.instance.extra_myopathy)

            adult_accomp_dis = ExtraAccompanyingDisease.\
                extra_accompanying_choices[-1]

            self.fields['other_accomp'].choices = [
                (ExtraAccompanyingDisease.extra_accompanying_choices.index(
                    adult_accomp_dis)+1, adult_accomp_dis[1])]

        else:
            gen_chars.remove('smoker')
            gen_chars.remove('alcohol')
            self.fields['other_accomp'].choices = [
                (indx+1, val[1]) for indx, val in
                enumerate(
                    ExtraAccompanyingDisease.extra_accompanying_choices[:-1])]
            self.fields['extra_myopathy'].label = "Άλλο: "
            self.fields['extra_myopathy'].widget.choices = [
                (indx or "", val[1]) for indx, val in
                enumerate([('', '---------')] + list(
                    ExtraMyopathy.extra_myopathy_choices[:-1]))]

        self.sections_fields = [("Γενικά Χαρακτηριστικά", self.names_to_fields(
                                    gen_chars)),
                                ("Διευκρίνιση Πάθησης", self.names_to_fields(
                                    self.underlying_dis)),
                                ("Συνοδά Νοσήματα", self.names_to_fields(
                                    accomp_dis)),
                                ("Πρόσθετες Πληροφορίες", self.names_to_fields(
                                    additional_info))
                                ]

        # If patient's condition is "ΣΑΥΥ",
        # remove section "Διευκρίνιση Πάθησης"
        if self.instance.visit.pat_id.pat_condition.pat_condition == "ΣΑΥΥ":
            self.sections_fields.pop(1)

    def names_to_fields(self, names_lst):
        """ Translate field names to real fields.
        Return form fields coresponding to the names in names_lst
        """
        return [self[fld_name] for fld_name in names_lst]

    def clean_other_accomp(self):
        other_accomp = self.cleaned_data.get('other_accomp')

        if len(other_accomp) > 2:
            self.add_error('other_accomp',
                           "Μπορείτε να επιλέξετε μέχρι δύο νοσήματα.")

        return other_accomp

    def clean(self):
        extra_myo = bool(self.data.get('extra_myopathy', None))
        super(CharacteristicsForm, self).clean()
        cleaned_data = self.cleaned_data

        if self.instance.visit.pat_id.pat_condition.pat_condition == "ΣΑΥΥ":
            cleaned_data['sayy'] = True

        if not self.instance.visit.pat_id.adult:
            del self._errors['smoker']
            del self._errors['alcohol']
            cleaned_data['smoker'] = BadHabit.objects.get(
                bad_habit_status="ΟΧΙ")

            cleaned_data['alcohol'] = BadHabit.objects.get(
                bad_habit_status="ΟΧΙ")

        else:
            if 'extra_myopathy' in self._errors:
                del self._errors['extra_myopathy']
            # If false return None else the record corresponding to ΑΛΛΟ
            adult_other_myopathy = ExtraMyopathy.extra_myopathy_choices[-1]
            cleaned_data['extra_myopathy'] = [
                None,
                ExtraMyopathy.objects.get(myopathy=adult_other_myopathy[0])][
                    int(extra_myo)]

        return cleaned_data

    def is_valid(self):
        super(CharacteristicsForm, self).is_valid()

        # Get all fields filled in, as far as underlying disease is concerned
        underlying_flds_filled = [self.cleaned_data.get(fld) for
                                  fld in self.underlying_dis]
        num_underlying = len(list(filter(lambda fld: fld is not False
                                         and fld is not None,
                                         underlying_flds_filled)))

        if num_underlying == 0 or num_underlying > 3:
            possible_errors = [
                "Πρέπει να δηλωθεί τουλάχιστον μία διευκρίνιση πάθησης",
                "Μπορούν να δηλωθούν το πολύ τρεις διευκρινίσεις πάθησης"]

            self.add_error(None, possible_errors[1 - (not num_underlying)])
        return not self._errors


class VentilationForm(CustomModelForm):

    class Meta:
        model = PatientVentilation
        exclude = ['visit']
        widgets = {
            'ventilation_type': forms.RadioSelect(attrs={
                'class': 'list-inline',
            },),
            'treatment_provider': forms.RadioSelect(attrs={
                'class': 'list-inline',
            },),
            'tracheostomy': forms.RadioSelect(attrs={
                'class': 'list-inline',
            },),
            'support_org_type': forms.RadioSelect(attrs={
                'class': 'list-inline',
            },),
        }

    def __init__(self, *args, **kwargs):
        super(VentilationForm, self).__init__(*args, **kwargs)
        self.instance = kwargs.pop('instance', None)

        gen_info = ['ventilation_status', 'ventilation_type',
                    'invasive_ventilation', 'ventilation_reason',
                    'treatment_provider', 'support_org_type']

        self.home_usage = ['xoth', 'xoth_hours_24', 'ventilation_hours',
                      'period_of_usage', 'application_instructions',
                      'physiotherapy_instructions', 'emergency_instructions',
                      'family_education', 'certified_education']

        if self.instance.visit.pat_id.pat_condition.pat_condition ==\
                "ΤΡΑΧΕΙΟΣΤΟΜΙΑ":
            gen_info.insert(3, 'tracheostomy')

        self.sections_fields = [("Γενικά Στοιχεία", self.names_to_fields(
                                        gen_info)),
                                ("Οδηγίες για Χρήση στο σπίτι",
                                self.names_to_fields(self.home_usage)),
                                ]

        previous_visits = PatientVisit.objects.filter(
            pat_id=self.instance.visit.pat_id,
            visit_date__lt=self.instance.visit.visit_date) \
            .order_by('-visit_date')

        if previous_visits:
            # Initialize fields for "Οδηγίες για Χρήση στο σπίτι"
            # to last_visit's values
            try:
                # Patient's latest visit ventilation record
                last_pventilation = PatientVentilation.objects.get(
                    visit=previous_visits.first())
                for fld in self.home_usage:
                    self[fld].initial = getattr(last_pventilation, fld)


            # If previous patient-ventilation has not be filled in, pass
            except PatientVentilation.DoesNotExist:
                pass

    def clean(self):
        super(VentilationForm, self).clean()
        data = self.cleaned_data

        # If ventilation type is not invasive, there is no need
        # for invasive_ventilation field to be filled
        if 'ventilation_type' not in self.cleaned_data or\
            self.cleaned_data.get(
                'ventilation_type').ventilation_type != "ΕΠΕΜΒΑΤΙΚΟΣ":
            data['invasive_ventilation'] = None

        if 'treatment_provider' in self.cleaned_data and \
                self.cleaned_data.get('treatment_provider').provider == 'ΜΕΘ':
            data['xoth'] = None
            data['xoth_hours_24'] = None
            data['ventilation_hours'] = None
            data['period_of_usage'] = None
#         if self.instance.visit.pat_id.pat_condition.pat_condition !=\
#                 "ΤΡΑΧΕΙΟΣΤΟΜΙΑ":
        return data

    def is_valid(self):
        super(VentilationForm, self).is_valid()

        # If ventilation type is not invasive, there is no need
        # for invasive_ventilation field to be filled
        if 'ventilation_type' not in self.cleaned_data or\
            self.cleaned_data.get(
                'ventilation_type').ventilation_type != "ΕΠΕΜΒΑΤΙΚΟΣ":
                if 'invasive_ventilation' in self._errors:
                    del self._errors['invasive_ventilation']

        if self.instance.visit.pat_id.pat_condition.pat_condition !=\
                "ΤΡΑΧΕΙΟΣΤΟΜΙΑ":
            del self._errors['tracheostomy']

        # In ΜΕΘ selection case, delete validation errors for the dependent fields
        if 'treatment_provider' in self.cleaned_data and \
                self.cleaned_data.get('treatment_provider').provider == 'ΜΕΘ':
            probable_error_fields = ['xoth', 'xoth_hours_24', 'ventilation_hours', 'period_of_usage']

            # Find which of the probable_error_fields exist in form's validation errors and remove
            # them from error dict
            valid_error_fields = filter(lambda el: el in self._errors, probable_error_fields)
            for err in valid_error_fields:
                del self._errors[err]

        return not self._errors

    def names_to_fields(self, names_lst):
        """ Translate field names to real fields.
        Return form fields coresponding to the names in names_lst
        """
        return [self[fld_name] for fld_name in names_lst]


class BreathAndSleepTestForm(CustomModelForm):
    has_symptoms = forms.ChoiceField(required=True, label="Έχει κλινικά συμπτώματα:",
                                     initial=None,
                                     choices=[(True, 'Ναι'), (False, 'Όχι')],
                                     widget=forms.RadioSelect(attrs={
                                         'class': 'list-inline',
                                     },))

    class Meta:
        model = BreathAndSleepTest
        exclude = ['visit']
        widgets = {
            'clinical_symptoms': forms.CheckboxSelectMultiple,
        }
        help_texts = {
            'psg_n1': 'Ποσοστό επί τοις εκατό % του TST',
            'psg_n2': 'Ποσοστό επί τοις εκατό % του TST',
            'psg_n3': 'Ποσοστό επί τοις εκατό % του TST',
            'psg_rem': 'Ποσοστό επί τοις εκατό % του TST',
        }

    def __init__(self, *args, **kwargs):
        super(BreathAndSleepTestForm, self).__init__(*args, **kwargs)
        # self.instance = kwargs.pop('instance', None)

        # self.fields['has_symptoms'].initial = None

        estimations = ['clinical_symptoms', 'daytime_hypercapnia',
                       'nocturnal_hypoventilation', 'hypoxemia']

        self.breath_tests = ['fvc_l', 'fvc_perc', 'fev1_l', 'fev_perc', 'fev1_fvc',
                        'fev25_75', 'ph', 'po2', 'pco2', 'h3co2', 'pins',
                        'pex', 'snip', 'pcf']
        # sleep_tests = ['overnight_oximetry', 'level_three_rec',
        #                'polysomnography', 'capnometry', 'other']

        self.sleep_oxy_tests = ['avsao2_oxy', 'minsao2_oxy', 't90_oxy', 'odi_oxy']

        self.sleep_br_tests = ['record_duration', 'ahirdi_br', 'avsao2_br',
                          'minsao2_br', 't90_br', 'odi_br']

        self.sleep_psg_tests = ['psg_trt', 'psg_tst', 'psg_sl', 'psg_se', 'psg_ai',
                           'waso', 'psg_n1', 'psg_n2', 'psg_n3', 'psg_rem', 'psg_snore',
                           'psg_ahirdi', 'psg_avsao2', 'psg_minsao2', 'psg_t90', 'psg_odi']

        self.sections_fields = [
            ("Εκτίμηση", [("", self.names_to_fields(estimations))]),
            ("Εξετάσεις Αναπνευστικής Λειτουργίας",
                [("", self.names_to_fields(self.breath_tests))]),
            ("Εξετάσεις Ύπνου",
                [("", self.names_to_fields(['overnight_oximetry'])),
                 ("Δείκτες Οξυμετρίας",
                    self.names_to_fields(self.sleep_oxy_tests)),
                 ("", self.names_to_fields(['level_three_rec'])),
                 ("Δείκτες Καταγραφής Τύπου ΙΙΙ",
                    self.names_to_fields(self.sleep_br_tests)),
                 ("", self.names_to_fields(['polysomnography'])),
                 ("Δείκτες Πολυπνογραφίας",
                    self.names_to_fields(self.sleep_psg_tests)),
                 ("", self.names_to_fields(['capnometry', 'other'])),
                 ])
        ]

    def names_to_fields(self, names_lst):
        """ Translate field names to real fields.
        Return form fields coresponding to the names in names_lst
        """
        return [self[fld_name] for fld_name in names_lst]

    def clean(self):
        super(BreathAndSleepTestForm, self).clean()
        data = self.cleaned_data

        # Return None for the fields concerning the sleep tests
        # that have not been carried out (overnight_oximetry,
        # level_three_rec, polysomnography)

        overnight_oximetry = self.cleaned_data.get("overnight_oximetry")
        level_three_rec = self.cleaned_data.get("level_three_rec")
        polysomnography = self.cleaned_data.get("polysomnography")

        has_symptoms = self.cleaned_data.get("has_symptoms")

        if has_symptoms=='False':
            data['clinical_symptoms'] = []

        if not overnight_oximetry:
            for fld_name in self.sleep_oxy_tests:
                data[fld_name] = None

        if not level_three_rec:
            for fld_name in self.sleep_br_tests:
                data[fld_name] = None

        if not polysomnography:
            for fld_name in self.sleep_psg_tests:
                data[fld_name] = None

        return data

    def is_valid(self):
        super(BreathAndSleepTestForm, self).is_valid()

        # If  doc_awareness is not Έκτακτη Ενημέρωση, there is no need
        # for emerging_awareness field to be filled in
        overnight_oximetry = self.cleaned_data.get("overnight_oximetry")
        level_three_rec = self.cleaned_data.get("level_three_rec")
        polysomnography = self.cleaned_data.get("polysomnography")

        has_symptoms = self.cleaned_data.get("has_symptoms")

        if has_symptoms=='False':
            del self._errors['clinical_symptoms']

        if not overnight_oximetry:
            for fld_name in self.sleep_oxy_tests:
                if fld_name in self._errors:
                    del self._errors[fld_name]

        if not level_three_rec:
            for fld_name in self.sleep_br_tests:
                if fld_name in self._errors:
                    del self._errors[fld_name]

        if not polysomnography:
            for fld_name in self.sleep_psg_tests:
                if fld_name in self._errors:
                    del self._errors[fld_name]

        return not self._errors


class SearchPatientForm(forms.Form):
    patient_code = forms.CharField(
        label="Αναγνωριστικό ασθενούς: ",
        max_length=11,
        required=True,
        validators=[pat_id_validator],
        widget=forms.TextInput({"class": "form-control"}))


class AddPatientForm(forms.Form):
    patient_center = forms.ChoiceField(label="Επιλογή Κέντρου:",
                                       widget=forms.Select(
                                           {"class": "custom-select"}))

    def __init__(self, *args, **kwargs):
        centers = kwargs.pop('centers', None)
        super(AddPatientForm, self).__init__(*args, **kwargs)

        self.fields['patient_center'].choices = [
            (choice.code, choice) for choice in centers]


class DeviceTestingInfoForm(CustomModelForm):
    daily_usage_hours = forms.FloatField(
        label="Ώρες ημερήσιας χρήσης από ασθενή",
        help_text="Ο υπολογισμός αυτού του πεδίου γίνεται αυτόματα")

    class Meta:
        model = DeviceTestingInfo
        fields = ['ma_type', 'dev_sel', 'manufacturer', 'serial_number',
                  'usage_hours', 'daily_usage_hours', 'humidifier',
                  'mask_type', 'technical_check', 'check_cause',
                  'checked_by', 'doc_informed', 'additional_info']

    def __init__(self, *args, **kwargs):
        super(DeviceTestingInfoForm, self).__init__(*args, **kwargs)
        self.fields['daily_usage_hours'].widget.attrs['readonly'] = True

    def clean(self):
        super(DeviceTestingInfoForm, self).clean()
        data = self.cleaned_data

        # If ventilation type is EMA, there is no need
        # for mask_type field to be filled
        if 'ma_type' not in self.cleaned_data or \
                self.cleaned_data.get('ma_type').type == "ΕΜΑ":
            data['mask_type'] = None

        if not self.cleaned_data['technical_check']:
            data['check_cause'] = None
            data['checked_by'] = None

        return data

    def is_valid(self):
        super(DeviceTestingInfoForm, self).is_valid()

        # If ventilation type is EMA, there is no need
        # for mask_type field to be filled
        if 'ma_type' not in self.cleaned_data or \
                self.cleaned_data.get('ma_type').type == "ΕΜΑ":
            if 'mask_type' in self._errors:
                del self._errors['mask_type']

        # If technical check has not been made, no need
        # for check_cause and checked by fields to be filled
        if not self.cleaned_data['technical_check']:
            if 'check_cause' in self._errors:
                del self._errors['check_cause']
            if 'checked_by' in self._errors:
                del self._errors['checked_by']

        print(self._errors)

        return not self._errors


class HelpAtHomeForm(CustomModelForm):

    class Meta:
        model = HelpAtHome

        fields = ['care_place', 'patient_status', 'doctor_visit',
                  'nurse_visit', 'local_health_care_provider', 'fiap',
                  'doc_awareness', 'emerging_awareness',
                  'frequent_family_retrain', 'life_quality_assessment']
        widgets = {
            'care_place': forms.RadioSelect(
                attrs={
                    'class': 'radio-inline',
                }
            )
        }

    def clean(self):
        super(HelpAtHomeForm, self).clean()
        data = self.cleaned_data

        # If  doc_awareness is not Έκτακτη Ενημέρωση, there is no need
        # for emerging_awareness field to be filled in
        cd_da = self.cleaned_data.get('doc_awareness')
        if cd_da and cd_da.status != "EKTAKTH ΕΝΗΜΕΡΩΣΗ":
            data['emerging_awareness'] = None
        return data

    def is_valid(self):
        super(HelpAtHomeForm, self).is_valid()

        # If  doc_awareness is not Έκτακτη Ενημέρωση, there is no need
        # for emerging_awareness field to be filled in
        cd_da = self.cleaned_data.get('doc_awareness')
        if cd_da and cd_da.status != "EKTAKTH ΕΝΗΜΕΡΩΣΗ":
            if 'emerging_awareness' in self._errors:
                    del self._errors['emerging_awareness']
        return not self._errors


class ICUForm(CustomModelForm):
    death_date = forms.DateField(
        label="Ημερομηνία Θανάτου: ",
        widget=forms.DateInput(
                format=('%d/%m/%Y'),
                attrs={
                    'min': '-48m',
                    'max': '+0d',
                    'placeholder': 'Επιλέξτε ημερομηνία',
                    'class': 'datepicker',
                },))

    death_cause = forms.ChoiceField(
        label="Αιτία Θανάτου: ",
        choices=(('', '-------'),)+DeathCause.death_cause_choices,
        required=True,)

    class Meta:
        model = ICU
        exclude = ['visit']
        widgets = {
            'coexisting_diseases': forms.CheckboxSelectMultiple,
            'complications': forms.CheckboxSelectMultiple,
        }

    def __init__(self, *args, **kwargs):
        super(ICUForm, self).__init__(*args, **kwargs)
        self.instance = kwargs.pop('instance', None)
        try:
            if self.instance.visit.pat_state.pat_status\
                    and self.instance.visit.pat_state.pat_status.pat_status \
                    == "ΘΑΝΑΤΟΣ":
                self['death_date'].initial = self.instance.visit.\
                    pat_state.date_of_death
                self['death_cause'].initial = self.instance.visit.\
                    pat_state.cause_of_death.death_cause
        except PatientState.DoesNotExist:
            pass

    def clean(self):
        super(ICUForm, self).clean()
        data = self.cleaned_data
        # If icu_outcome is not death, cause and date of death should be null (none)
        if 'icu_outcome' in self.cleaned_data:
            if self.cleaned_data.get('icu_outcome').outcome != "ΘΑΝΑΤΟΣ":
                data['death_date'] = None
                data['death_cause'] = None
            else:
                data['icu_exit_transfer'] = None
        return data

    def is_valid(self):
        super(ICUForm, self).is_valid()

        # Get at least one of the three severity fields filled in
        severity_flds_filled = [self.cleaned_data.get(fld) for
                                fld in ['apache_II', 'sofa', 'tiss']]

        num_severity_filled = len(list(filter(lambda fld: fld is not None,
                                              severity_flds_filled)))

        if num_severity_filled < 1:
            self.add_error(
                None, "Πρέπει να συμπληρωθεί τουλάχιστον "
                "ένας από τους δείκτες APACHE II, SOFA και TISS")

        icu_outcome = self.cleaned_data.get('icu_outcome')
        if icu_outcome:
            if icu_outcome.outcome == 'ΘΑΝΑΤΟΣ':
                if 'icu_exit_transfer' in self._errors:
                    del self._errors['icu_exit_transfer']

                if self.instance:
                    cur_visit_date = self.instance.visit.visit_date
                    patient = self.instance.visit.pat_id
                    if (PatientVisit.objects.filter(
                            pat_id=patient, visit_date__gt=cur_visit_date)):
                        self.add_error(
                            'icu_outcome',
                            "Δεν μπορεί να πραγματοποιηθεί μεταβολή της έκβασης του \
                            ασθενούς στην τιμή 'Θάνατος', ενώ υπάρχουν \
                            μεταγενέστερες της παρούσας επισκέψεις.")
                    else:
                        death_date = self.cleaned_data.get('death_date')
                        if death_date and cur_visit_date < death_date:
                            self.add_error(
                                'death_date',
                                "Η ημερομηνία θανάτου του ασθενούς, δεν μπορεί να είναι\
                            μεταγενέστερη της παρούσας επίσκεψης.")

            else:
                if 'death_cause' in self._errors:
                    del self._errors['death_cause']
                if 'death_date' in self._errors:
                    del self._errors['death_date']
        else:
            if 'icu_exit_transfer' in self._errors:
                    del self._errors['icu_exit_transfer']
            if 'death_cause' in self._errors:
                    del self._errors['death_cause']
            if 'death_date' in self._errors:
                del self._errors['death_date']

        return not self._errors


class ExportSelectForm(forms.Form):
    export_centers = forms.MultipleChoiceField(
        label="Επιλογή κέντρων",
        widget=forms.CheckboxSelectMultiple)

    et = ExportTool()
    objs = et.obj_fields.keys()
#     OBJECTS = list(zip(*[objs]*2))
#     objects_to_export = forms.MultipleChoiceField(
#         label="Εξαγωγή οντοτήτων",
#         widget=forms.CheckboxSelectMultiple,
#         choices=OBJECTS)

    def __init__(self, *args, **kwargs):
        centers = kwargs.pop('centers', None)
        super(ExportSelectForm, self).__init__(*args, **kwargs)
        self.fields['export_centers'].choices = [
            (choice.code, choice) for choice in centers]
        for obj_name in self.objs:
            CHOICES = list(zip(*[list(self.et.obj_fields[obj_name].keys())]*2))
            self.fields[obj_name] = forms.MultipleChoiceField(
                label=obj_name,
                widget=forms.CheckboxSelectMultiple,
                choices=CHOICES, required=False)
#             self.fields[obj_name].widget.attrs.update({
#                     'class': 'special-check-box',})

#     def clean(self):
#         data = {}
#         fld_names = ['export_centers']+list(self.objs)
#         for fld_name in fld_names:
#             fld_data = self.data.get(fld_name)
#             print("Fld data: ", fld_data)
#             data[fld_name] = fld_data
#             if fld_data and fld_name in fld_data:
#                 print("in")
#                 data[fld_name].pop(0)
# 
# #         map(lambda fld_name: self.data.get(fld_name).pop(0) if fld_name in self.data.get(fld_name) else "", fld_names)
#         print(data)
#         return data
#         super(ExportSelectForm, self).clean()

#     def is_valid(self):
#         print(self.data)
#         map(lambda obj_name: self.data[obj_name].pop(0) if obj_name in self.data[obj_name] else None, self.objs)
#         super(ExportSelectForm, self).is_valid()
#         # Remove invalid errors caused from custom card-header checkboxes
#         print(self._errors)
#         if 'export_centers' in self._errors:
#             print(self._errors.get("export_centers", self.error_class()))
# #             del self._errors['export_centers']
#         map(lambda obj_name: self._errors.pop(obj_name, None), self.objs)
#         print(self._errors)
#         return not self._errors
 
#             else:
#                 if 'death_cause' in self._errors:
#                     del self._errors['death_cause']
#                 if 'death_date' in self._errors:
#                     del self._errors['death_date']
