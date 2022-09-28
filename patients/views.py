import logging
import requests
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.shortcuts import HttpResponseRedirect
from django.shortcuts import redirect

from patients.errors_redirects import forbidden_redirect

from patients.forms import AddPatientForm
from patients.forms import BreathAndSleepTestForm
from patients.forms import CaregiverForm
from patients.forms import CharacteristicsForm
from patients.forms import DemographicsForm
from patients.forms import DeviceTestingInfoForm
from patients.forms import ExportSelectForm
from patients.forms import HelpAtHomeForm
from patients.forms import ICUForm
from patients.forms import RegisterForm
from patients.forms import SearchPatientForm
from patients.forms import StateForm
from patients.forms import VentilationForm
from patients.forms import VisitForm

from patients.helper_modules import authorized_centers
from patients.helper_modules import delete_db_rec
from patients.helper_modules import max_old_center_patient

from centers.models import Doctor
from patients.models import BreathAndSleepTest, DeathCause, PatientStatus
from patients.models import Caregiver
from patients.models import DeviceTestingInfo
from patients.models import HelpAtHome
from patients.models import ICU
from patients.models import PatientCharacteristics
from patients.models import PatientState
from patients.models import PatientVentilation

from patients.models import PatientVisit
from patients.models import Patient


log = logging.getLogger(__name__)

# Create your views here.
@login_required
def index(request):
    """ The index page
    """

    # If it is the first sing in for currnet user,
    # make him/her change his/her password
    # if request.user.doctor.force_password_change:
    #     return redirect('password_change')

    # Take user/doctor to search_add page otherwise
    return redirect('search_add')


@login_required
def search_add_patient(request):
    """ Doctor searching for a specific patient, or adding a new one.
    In case of searching, patient and doctor must belong to the same center.
    """

    doctor = request.user

    # Make sure user is a doctor
    doctor = get_object_or_404(Doctor, user=doctor)

    # Get all the codes of the centers this doctor belongs to
    doc_centers = doctor.centers.all()

    # Initialise forms. In case of POST request, the proper form will change
    sform = SearchPatientForm(label_suffix='')
    aform = AddPatientForm(centers=doc_centers, label_suffix='')

    if request.method == 'POST':

        # Depending on which form is used, the proper tuple will be kept
        field_value = ('patient_code', request.POST.get('patient_code'))\
            if 'patient_code' in request.POST\
            else ('patient_center', request.POST.get('patient_center'))\
            if 'patient_center' in request.POST else ('other', None)

        # This is a search action
        if field_value[0] == 'patient_code':
            sform = SearchPatientForm(request.POST, label_suffix='')
            if sform.is_valid():
                does_not_exist = False
                try:
                    patient = Patient.objects.get(pat_id=field_value[1])
                except Patient.DoesNotExist:
                    does_not_exist = True

                # If none of the care centers that the patient has been at,
                # is a center that the doctor is working at, or the patient
                # does not exist in the system at all, feed form with an error
                if does_not_exist or not authorized_centers(
                        patient.care_centers.all(), doc_centers):
                    sform.add_error(
                        'patient_code',
                        'Δεν υπάρχει ασθενής με αυτό το αναγνωριστικό που να ανήκει\
                        σε κάποιο από τα κέντρα στα οποία εργάζεστε.')
                else:
                    return redirect('pmenu', patient_id=patient.id)

        # This is an add action
        if field_value[0] == 'patient_center':
            aform = AddPatientForm(request.POST,
                                   centers=doc_centers, label_suffix='')

            if aform.is_valid():
                center_patients = Patient.objects.filter(
                    pat_id__iregex=r""+field_value[1]+"[A-Z]{2}[0-9]{6}")

                # Get the max pat_id from old patients for this center
                max_old_center_pat = max_old_center_patient(field_value[1])

                center_patients = list(map(
                    lambda cp: cp.pat_id, center_patients)) + (
                    [max_old_center_pat] if max_old_center_pat else [])

                # Get the maximum patient id from this center
                max_center_patient_id = int(max(map(
                    lambda pid: pid[5:], center_patients), default=0))

                # The patient id for the next patient to be created for the
                # specific center
                next_pat_id = "{}MV{:06d}".format(field_value[1],
                                                  max_center_patient_id+1)
                return redirect('pregistration', patient_code=next_pat_id)

    context = {
        'title': "Καταγραφή Ασθενών με χρόνια αναπνευστικά νοσήματα",
        'subtitle': "και χρήση αναπνευστικών συσκευών στο σπίτι",
        'sform': sform,
        'aform': aform,
    }
    return render(request, 'patients/search_add_patient.html', context)


@login_required
def patient_demographics(request, patient_id):
    """ Patient Demographics Form """

    if not request.META.get('HTTP_REFERER'):
        return forbidden_redirect(request)

    patient = get_object_or_404(Patient, pk=patient_id)

    #  If patient is an adult, there is no caregiver for that patient
    caregiver = None

    # If patient is not an adult, there should be a caregiver
    if not patient.adult:
        # Get patient's (specific) caregiver
        # If no caregiver appointed for non-adult patient
        # or caregiver does not exist,  create one
        caregiver = patient.caregiver or Caregiver()

    delete_switch = 'enabled' if all([
        patient.adult, patient.residence, patient.profession, patient.education
        ]) or all([patient.caregiver, patient.residence]) else 'disabled'

    forms = []
    if request.method == 'POST':

        if caregiver:  # Patient not an adult
            cgform = CaregiverForm(request.POST, instance=caregiver,
                                   label_suffix='')
            forms.append(cgform)

        pform = DemographicsForm(request.POST, instance=patient,
                                 label_suffix='')
        forms.append(pform)

        tmp_objs = []

        validity = all(map(lambda f: f.is_valid(), forms))

        if validity:  # All forms were valid
            for form in forms:
                tmp_objs.append(form.save(commit=False))
            tmp_objs.reverse()  # Put patient object first in any case

            # Update patient's field values and save all changes to database
            patient.residence = tmp_objs[0].residence
            patient.profession = tmp_objs[0].profession
            patient.education = tmp_objs[0].education
            patient.comment = tmp_objs[0].comment

            if len(tmp_objs) == 2:
                # Save profession, in case a new one was added
                # (this code should probably be inactive now)
                patient.caregiver, _ = Caregiver.objects.get_or_create(
                    profession=tmp_objs[1].profession,
                    education=tmp_objs[1].education,
                    relation_to_patient=tmp_objs[1].relation_to_patient)

            patient.save()

            messages.success(
                request,
                "Η ενημέρωση του συστήματος πραγματοποιήθηκε επιτυχώς!")

            return HttpResponseRedirect(request.path_info)

        else:
            messages.error(
                request,
                "Η ενημέρωση του συστήματος απέτυχε \
                λόγω λαθών στη φόρμα εισαγωγής.\
                Παρακαλώ προσπαθήστε ξανά!")

    elif request.method == 'DELETE':
        # Special 'delete', since you cannot delete whole patient
        # So update proper fields to null and if patient is a child
        # delete caregiver

        try:
            if patient.caregiver:
                tmp_caregiver = patient.caregiver
                patient.caregiver = None
                delete_db_rec(tmp_caregiver)

            patient.residence = None
            patient.profession = None
            patient.education = None
            patient.comment = None
            patient.save(update_fields=['residence', 'profession',
                                        'caregiver', 'education',
                                        'comment'])

            resp_status = 200
            resp_message = "Η διαγραφή ολοκληρώθηκε επιτυχώς!"
            resp = HttpResponse(
                content=resp_message,
                status=resp_status)

        except Exception:
            resp_status = 500
            resp_message = "Δυστυχώς η διαγραφή αυτή, δεν ήταν δυνατόν "\
                "να ολοκληρωθεί!"
            resp = HttpResponse(
                content=resp_message,
                status=resp_status)

        return resp

    # In case of GET method
    else:
        if caregiver:
            cgform = CaregiverForm(instance=caregiver, label_suffix='')
            forms.append(cgform)

        pform = DemographicsForm(instance=patient, label_suffix='')
        forms.append(pform)

    forms.reverse()  # So that they appear in the order we want in template
    context = {
        'title': "Καταγραφή Ασθενών με χρόνια αναπνευστικά νοσήματα",
        'subtitle': "και χρήση αναπνευστικών συσκευών στο σπίτι",
        'patient_id': patient_id,
        'delete_switch': delete_switch,
        'forms': forms,
    }
    return render(request, 'patients/patient_demographics.html', context)


@login_required
def patient_menu(request, patient_id=0, patient_visit_id=0):
    """ Patient Menu """

    def get_visits(patient):
        """ Update and return visits' list for this patient, in a proper format,
        order by reverse date.
        """

        # Return visits in proper/reverse order, or create a new one(the
        # initial visit) in case there are no visits yet
        visits = PatientVisit.objects.filter(
            pat_id=patient).order_by('-visit_date')

        if not visits:
            pat_visit = PatientVisit.objects.create(
                pat_id=patient,
                visit_date=patient.ma_subscription_date\
                           or datetime.today().strftime('%Y-%m-%d'))
            visits = PatientVisit.objects.filter(pk=pat_visit.pk)
        return visits

    def get_formatted_visits(visits):
        """ Return visits received as argument, in a proper format
        """
        visits = list(map(lambda indx_val: "Καταγραφή {} ({})"
                      .format(len(visits)-indx_val[0],
                              indx_val[1].visit_date.strftime("%d-%m-%Y")),
                      enumerate(visits))) +\
            ["Νέα Καταγραφή" if get_death_switch(visits) == 'enabled' else '']

        return visits

    def get_first_visit_switch(vis_date, visits):
        """ Return 'disabled' if this is the patient's first visit,
        'enabled' otherwise!
        """
        return 'disabled' if visits.last().visit_date == vis_date\
            else 'enabled'

    def get_death_switch(visits):
        """ Return 'disabled' if patient is already dead, 'enabled' otherwise!
        """
        return 'disabled' if PatientState.objects.filter(
            visit__in=visits, pat_status__pat_status="ΘΑΝΑΤΟΣ")\
            else 'enabled'

    def get_help_at_home_switch(patient, first_visit_switch):
        """ Return 'disabled' if patient suffers from sayy, 'enabled' otherwise!
        """
        return 'disabled' if first_visit_switch == 'disabled'\
            or not(patient.pat_condition) or patient.pat_condition.pat_condition == "ΣΑΥΥ" else 'enabled'

    def get_ventilation_switch(patient, first_visit_switch):
        """ Return 'disabled' in case patient's condition is tracheostomy or
        current visit is the first one, 'enabled' otherwise!
        """
        return 'disabled' if first_visit_switch == 'disabled'\
            or not(patient.pat_condition) or patient.pat_condition.pat_condition \
            in ["ΤΡΑΧΕΙΟΣΤΟΜΙΑ", "ΣΑΥΥ"]\
            else 'enabled'

    def get_device_switch(patient, first_visit_switch):
        """ Return 'disabled' in case patient's condition is tracheostomy or
        current visit is the first one, 'enabled' otherwise!
        """
        return 'disabled' if first_visit_switch == 'disabled'\
            or not(patient.pat_condition) or patient.pat_condition.pat_condition == "ΤΡΑΧΕΙΟΣΤΟΜΙΑ"\
            else 'enabled'

    def get_icu_switch(patient):
        """ Return true if patient's icu field is True, false otherwise!
        """
        return patient.icu

    if not request.META.get('HTTP_REFERER'):
        return forbidden_redirect(request)

    pat_visit = None if not patient_visit_id else\
        get_object_or_404(PatientVisit, pk=patient_visit_id)

    # Get all patient's visits in reverse order
    patient = get_object_or_404(Patient, pk=patient_id) if patient_id\
        else pat_visit.pat_id
    visits = get_visits(patient)
    fmted_visits = get_formatted_visits(visits)


    # Initialise to the latest visit
    v_date = pat_visit.visit_date if pat_visit else visits.first().visit_date\
        if visits else datetime.now().date()

    if request.method == 'POST':

        # Visit date with slashes. An invalid date in case of empty visit_date
        request_date = request.POST.get('visit_date')
        
        v_date = datetime.strptime(request_date, "%d/%m/%Y").date()\
            if request_date else v_date

        # The patient-visit instance to use for the form.
        # Create it if it does not exist
        try:
            pat_visit = visits.get(visit_date=v_date)
        except PatientVisit.DoesNotExist:
            pat_visit = PatientVisit(
                pat_id=patient,
                visit_date=v_date)

        vform = VisitForm(request.POST, instance=pat_visit, label_suffix='')

        if vform.is_valid():
            pat_visit = vform.save()

            # Update visits
            visits = get_visits(patient)
            fmted_visits = get_formatted_visits(visits)

        else:
            messages.error(
                request,
                "Παρακαλώ επιλέξτε μια έγκυρη ημερομηνία καταγραφής!")

    else:
        pat_visit, _ = PatientVisit.objects.get_or_create(
                pat_id=patient,
                visit_date=v_date)

        vform = VisitForm(instance=pat_visit, label_suffix='')

    first_visit_switch = get_first_visit_switch(v_date, visits)
    ventilation_switch = get_ventilation_switch(patient, first_visit_switch)
    device_switch = get_device_switch(patient, first_visit_switch)
    death_switch = get_death_switch(visits)
    help_at_home_switch = get_help_at_home_switch(patient, first_visit_switch)
    icu_switch = get_icu_switch(patient)

    cur_visit_date = "".join(vd for vd in fmted_visits
                             if v_date.strftime("%d-%m-%Y") in vd)

    context = {
        'patient_id': patient.pk,
        'patient_code': patient.pat_id,
        'title': "Καταγραφή Ασθενών με χρόνια αναπνευστικά νοσήματα",
        'subtitle': "και χρήση αναπνευστικών συσκευών στο σπίτι",
        'fmted_visits': fmted_visits,
        'cur_visit_date': cur_visit_date,
        'first_visit_switch': first_visit_switch,
        'death_switch': death_switch,
        'help_at_home_switch': help_at_home_switch,
        'ventilation_switch': ventilation_switch,
        'device_switch': device_switch,
        'icu_switch': icu_switch,
        'pat_visit_id': pat_visit.pk,
        'vform': vform,
    }
    return render(request, 'patients/patient_menu.html', context)


@login_required
def patient_registration(request, patient_id=0, patient_code=""):
    """ Patient Registration Form
    """

    if not request.META.get('HTTP_REFERER'):
        return forbidden_redirect(request)

    # Registration process
    if patient_id == 0:
        patient = Patient(pat_id=patient_code)

    # Edit existing patient's profile, 404 if patient does not exist
    else:
        patient = get_object_or_404(Patient, pk=patient_id)

    if request.method == 'POST':
        rform = RegisterForm(request.POST, instance=patient, label_suffix='')

        if rform.is_valid():
            rform.save()
            messages.success(
                request,
                "Η ενημέρωση του συστήματος πραγματοποιήθηκε επιτυχώς!")

        else:
            messages.error(
                request,
                "Η ενημέρωση του συστήματος απέτυχε \
                λόγω λαθών στη φόρμα εισαγωγής.\
                Παρακαλώ προσπαθήστε ξανά!")

    else:
        rform = RegisterForm(label_suffix='', instance=patient)

    context = {
        'title': "Καταγραφή Ασθενών με χρόνια αναπνευστικά νοσήματα",
        'subtitle': "και χρήση αναπνευστικών συσκευών στο σπίτι",
        'patient_id': patient.pk,
        'delete_switch': 'disabled',
        'rform': rform,
    }
    return render(request, 'patients/patient_register.html', context)


@login_required
def patient_state(request, pat_visit_id):
    """ Patient State Form """

    if not request.META.get('HTTP_REFERER'):
        return forbidden_redirect(request)

    pat_visit = get_object_or_404(PatientVisit, pk=pat_visit_id)

    try:
        pat_state = PatientState.objects.get(visit=pat_visit)
    except PatientState.DoesNotExist:
        pat_state = PatientState(visit=pat_visit)

    delete_switch = 'disabled' if not pat_state.pk else 'enabled'

    if request.method == 'POST':
        psform = StateForm(request.POST,
                           instance=pat_state, label_suffix='')

        if psform.is_valid():
            psform.save()
            messages.success(
                request,
                "Η ενημέρωση του συστήματος πραγματοποιήθηκε επιτυχώς!")

            return HttpResponseRedirect(request.path_info)

        else:
            messages.error(
                request,
                "Η ενημέρωση του συστήματος απέτυχε \
                λόγω λαθών στη φόρμα εισαγωγής.\
                Παρακαλώ προσπαθήστε ξανά!")

    elif request.method == 'DELETE':
        return delete_db_rec(pat_state)

    else:
        psform = StateForm(label_suffix='', instance=pat_state)

    context = {
        'title': "Καταγραφή Ασθενών με χρόνια αναπνευστικά νοσήματα",
        'subtitle': "και χρήση αναπνευστικών συσκευών στο σπίτι",
        'pat_visit_id': pat_visit_id,
        'pat_visit_date': pat_visit.visit_date,
        'patient_id': pat_visit.pat_id.pk,
        'delete_switch': delete_switch,
        'psform': psform,
    }
    return render(request, 'patients/patient_state.html', context)


@login_required
def patient_characteristics(request, pat_visit_id):
    """ Patient Characteristics Form """

    if not request.META.get('HTTP_REFERER'):
        return forbidden_redirect(request)

    pat_visit = get_object_or_404(PatientVisit, pk=pat_visit_id)

    try:
        pat_chars = PatientCharacteristics.objects.get(visit=pat_visit)
    except PatientCharacteristics.DoesNotExist:
        pat_chars = PatientCharacteristics(visit=pat_visit)

    delete_switch = 'disabled' if not pat_chars.pk else 'enabled'

    if request.method == 'POST':
        pcform = CharacteristicsForm(request.POST,
                                     instance=pat_chars,
                                     label_suffix='')

        if pcform.is_valid():
            pcform.save()
            messages.success(
                request,
                "Η ενημέρωση του συστήματος πραγματοποιήθηκε επιτυχώς!")

            return HttpResponseRedirect(request.path_info)

        else:
            messages.error(
                request,
                "Η ενημέρωση του συστήματος απέτυχε \
                λόγω λαθών στη φόρμα εισαγωγής.\
                Παρακαλώ προσπαθήστε ξανά!")

    elif request.method == 'DELETE':
        return delete_db_rec(pat_chars)

    else:
        pcform = CharacteristicsForm(label_suffix='',
                                     instance=pat_chars)

    context = {
        'title': "Καταγραφή Ασθενών με χρόνια αναπνευστικά νοσήματα",
        'subtitle': "και χρήση αναπνευστικών συσκευών στο σπίτι",
        'pat_visit_id': pat_visit_id,
        'pat_visit_date': pat_visit.visit_date,
        'patient_id': pat_visit.pat_id.pk,
        'delete_switch': delete_switch,
        'pcform': pcform,
    }
    return render(request, 'patients/patient_characteristics.html', context)


@login_required
def patient_ventilation(request, pat_visit_id):
    """ Form concerning info and effectiveness of a ventilation system
    used by a patient. Filled in at every visit!
    """

    if not request.META.get('HTTP_REFERER'):
        return forbidden_redirect(request)

    pat_visit = get_object_or_404(PatientVisit, pk=pat_visit_id)

    try:
        pat_vent = PatientVentilation.objects.get(visit=pat_visit)
    except PatientVentilation.DoesNotExist:
        pat_vent = PatientVentilation(visit=pat_visit)

    delete_switch = 'disabled' if not pat_vent.pk else 'enabled'

    if request.method == 'POST':
        pcform = VentilationForm(request.POST,
                                 instance=pat_vent,
                                 label_suffix='')

        if pcform.is_valid():
            pcform.save()
            messages.success(
                request,
                "Η ενημέρωση του συστήματος πραγματοποιήθηκε επιτυχώς!")

            return HttpResponseRedirect(request.path_info)

        else:
            messages.error(
                request,
                "Η ενημέρωση του συστήματος απέτυχε \
                λόγω λαθών στη φόρμα εισαγωγής.\
                Παρακαλώ προσπαθήστε ξανά!")

    elif request.method == 'DELETE':
        return delete_db_rec(pat_vent)

    else:
        pcform = VentilationForm(label_suffix='',
                                 instance=pat_vent)

    context = {
        'title': "Καταγραφή Ασθενών με χρόνια αναπνευστικά νοσήματα",
        'subtitle': "και χρήση αναπνευστικών συσκευών στο σπίτι",
        'pat_visit_id': pat_visit_id,
        'pat_visit_date': pat_visit.visit_date,
        'patient_id': pat_visit.pat_id.pk,
        'delete_switch': delete_switch,
        'pcform': pcform,
    }
    return render(request, 'patients/patient_ventilation.html', context)


@login_required
def patient_breath_test(request, pat_visit_id):
    """ Form concerning the breath test results.
    Filled in at every visit!
    """

    if not request.META.get('HTTP_REFERER'):
        return forbidden_redirect(request)

    pat_visit = get_object_or_404(PatientVisit, pk=pat_visit_id)

    try:
        pat_test = BreathAndSleepTest.objects.get(visit=pat_visit)
    except BreathAndSleepTest.DoesNotExist:
        pat_test = BreathAndSleepTest(visit=pat_visit)

    delete_switch = 'disabled' if not pat_test.pk else 'enabled'

    if request.method == 'POST':
        bstform = BreathAndSleepTestForm(request.POST,
                                         instance=pat_test,
                                         label_suffix='')

        if bstform.is_valid():
            bstform.save()
            messages.success(
                request,
                "Η ενημέρωση του συστήματος πραγματοποιήθηκε επιτυχώς!")

            return HttpResponseRedirect(request.path_info)

        else:
            messages.error(
                request,
                "Η ενημέρωση του συστήματος απέτυχε \
                λόγω λαθών στη φόρμα εισαγωγής.\
                Παρακαλώ προσπαθήστε ξανά!")

    elif request.method == 'DELETE':
        return delete_db_rec(pat_test)

    # Get request
    else:
        bstform = BreathAndSleepTestForm(label_suffix='',
                                         instance=pat_test)

    context = {
        'title': "Καταγραφή Ασθενών με χρόνια αναπνευστικά νοσήματα",
        'subtitle': "και χρήση αναπνευστικών συσκευών στο σπίτι",
        'pat_visit_id': pat_visit_id,
        'pat_visit_date': pat_visit.visit_date,
        'patient_id': pat_visit.pat_id.pk,
        'delete_switch': delete_switch,
        'bstform': bstform,
    }
    return render(request, 'patients/patient_breath_test.html', context)


@login_required
def patient_device_testing(request, pat_visit_id):
    """ Form concerning device testing.
    Filled in at every visit!
    """

    if not request.META.get('HTTP_REFERER'):
        return forbidden_redirect(request)

    pat_visit = get_object_or_404(PatientVisit, pk=pat_visit_id)

    # Get previous (filled in for device), visit date
    prev_dev_visits = DeviceTestingInfo.objects.filter(
        visit__pat_id=pat_visit.pat_id,
    )

    prev_visit = PatientVisit.objects.filter(
        pat_dev_test__in=prev_dev_visits,
        visit_date__lt=pat_visit.visit_date).order_by('-visit_date').first()

    days_since_prev_visit = 1
    prev_usage_hours = 0

    is_new_device = False
    # Check whether it is a new device or not
    try:
        if pat_visit.pat_vent.ventilation_status.status == "ΑΛΛΑΓΗ ΣΥΣΚΕΥΗΣ":
            is_new_device = True
    except PatientVentilation.DoesNotExist:
        is_new_device = False

    # If there is no previous record of the device info, or patient gets a new device
    # do not get usage hours, there is no point
    if prev_visit and not is_new_device:
        try:
            prev_dev_test = DeviceTestingInfo.objects.get(visit=prev_visit)
            prev_usage_hours = prev_dev_test.usage_hours
        except DeviceTestingInfo.DoesNotExist:
            prev_usage_hours = 0
        # Days that have passed, since the previous visit
        days_since_prev_visit = (pat_visit.visit_date-prev_visit.visit_date).days

    try:
        dev_test = DeviceTestingInfo.objects.get(visit=pat_visit)
    except DeviceTestingInfo.DoesNotExist:
        dev_test = DeviceTestingInfo(visit=pat_visit)

    delete_switch = 'disabled' if not dev_test.pk else 'enabled'

    if request.method == 'POST':
        dtiform = DeviceTestingInfoForm(request.POST,
                                        instance=dev_test,
                                        label_suffix='')

        if dtiform.is_valid():
            dtiform.save()
            messages.success(
                request,
                "Η ενημέρωση του συστήματος πραγματοποιήθηκε επιτυχώς!")

            return HttpResponseRedirect(request.path_info)

        else:
            messages.error(
                request,
                "Η ενημέρωση του συστήματος απέτυχε \
                λόγω λαθών στη φόρμα εισαγωγής.\
                Παρακαλώ προσπαθήστε ξανά!")

    elif request.method == 'DELETE':
        return delete_db_rec(dev_test)

    # Get request
    else:
        dtiform = DeviceTestingInfoForm(label_suffix='',
                                        instance=dev_test)
    context = {
        'title': "Καταγραφή Ασθενών με χρόνια αναπνευστικά νοσήματα",
        'subtitle': "και χρήση αναπνευστικών συσκευών στο σπίτι",
        'pat_visit_id': pat_visit_id,
        'pat_visit_date': pat_visit.visit_date,
        'patient_id': pat_visit.pat_id.pk,
        'prev_usage_hours': prev_usage_hours,
        'days_since_prev_visit': days_since_prev_visit,
        'delete_switch': delete_switch,
        'dtiform': dtiform,
    }
    return render(request, 'patients/patient_device_testing.html', context)


@login_required
def patient_help_at_home(request, pat_visit_id):
    """ Form concerning help at home info.
    Filled in at every visit!
    """

    if not request.META.get('HTTP_REFERER'):
        return forbidden_redirect(request)

    pat_visit = get_object_or_404(PatientVisit, pk=pat_visit_id)

    try:
        help_at_home = HelpAtHome.objects.get(visit=pat_visit)
    except HelpAtHome.DoesNotExist:
        help_at_home = HelpAtHome(visit=pat_visit)

    delete_switch = 'disabled' if not help_at_home.pk else 'enabled'

    if request.method == 'POST':
        hahform = HelpAtHomeForm(request.POST,
                                 instance=help_at_home,
                                 label_suffix='')

        if hahform.is_valid():
            hahform.save()
            messages.success(
                request,
                "Η ενημέρωση του συστήματος πραγματοποιήθηκε επιτυχώς!")

            return HttpResponseRedirect(request.path_info)

        else:
            messages.error(
                request,
                "Η ενημέρωση του συστήματος απέτυχε \
                λόγω λαθών στη φόρμα εισαγωγής.\
                Παρακαλώ προσπαθήστε ξανά!")

    elif request.method == 'DELETE':
        return delete_db_rec(help_at_home)

    # Get request
    else:
        hahform = HelpAtHomeForm(label_suffix='',
                                 instance=help_at_home)

    context = {
        'title': "Καταγραφή Ασθενών με χρόνια αναπνευστικά νοσήματα",
        'subtitle': "και χρήση αναπνευστικών συσκευών στο σπίτι",
        'pat_visit_id': pat_visit_id,
        'pat_visit_date': pat_visit.visit_date,
        'patient_id': pat_visit.pat_id.pk,
        'delete_switch': delete_switch,
        'hahform': hahform,
    }
    return render(request, 'patients/patient_help_at_home.html', context)


@login_required
def patient_icu(request, pat_visit_id):
    """ Form concerning ICU!
    """

    if not request.META.get('HTTP_REFERER'):
        return forbidden_redirect(request)

    pat_visit = get_object_or_404(PatientVisit, pk=pat_visit_id)

    try:
        icu = ICU.objects.get(visit=pat_visit)
    except ICU.DoesNotExist:
        icu = ICU(visit=pat_visit)

    delete_switch = 'disabled' if not icu.pk else 'enabled'

    if request.method == 'POST':
        icuform = ICUForm(request.POST,
                          instance=icu,
                          label_suffix='')

        if icuform.is_valid():
            icuform.save()

            death_date = icuform.cleaned_data.get('death_date')
            try:
                death_cause = DeathCause.objects.get(
                    death_cause=icuform.cleaned_data.get('death_cause'))
            except DeathCause.DoesNotExist:
                death_cause = None

            try:
                pat_state = pat_visit.pat_state

            # Get or create not necessary for patient status
            except PatientState.DoesNotExist:
                pat_state = PatientState(
                    visit=pat_visit,
                    pat_status=PatientStatus.objects.get_or_create(
                        pat_status="ΘΑΝΑΤΟΣ")[0])


            pat_state.pat_status = PatientStatus.objects.get(pat_status="ΘΑΝΑΤΟΣ") \
                if icu.icu_outcome.outcome == "ΘΑΝΑΤΟΣ" else None
            pat_state.date_of_death = death_date
            pat_state.cause_of_death = death_cause
            pat_state.save()

            messages.success(
                request,
                "Η ενημέρωση του συστήματος πραγματοποιήθηκε επιτυχώς!")

            return HttpResponseRedirect(request.path_info)

        else:
            messages.error(
                request,
                "Η ενημέρωση του συστήματος απέτυχε \
                λόγω λαθών στη φόρμα εισαγωγής.\
                Παρακαλώ προσπαθήστε ξανά!")

    elif request.method == 'DELETE':
        del_ret_icu = delete_db_rec(icu)

        # Case of death as far as icu_outcome is concerned
        try:
            pat_state = pat_visit.pat_state
        except PatientState.DoesNotExist:
            pat_state = None

        if pat_state:
            del_ret_state = delete_db_rec(pat_state)

        return del_ret_icu

    # Get request
    else:
        icuform = ICUForm(label_suffix='',
                          instance=icu)

    context = {
        'title': "Καταγραφή Ασθενών με χρόνια αναπνευστικά νοσήματα",
        'subtitle': "και χρήση αναπνευστικών συσκευών στο σπίτι",
        'pat_visit_id': pat_visit_id,
        'pat_visit_date': pat_visit.visit_date,
        'patient_id': pat_visit.pat_id.pk,
        'delete_switch': delete_switch,
        'icuform': icuform,
    }
    return render(request, 'patients/patient_icu.html', context)


@login_required
def export(request):
    """ Form for choosing which objects and which fields to export
    """

    if not request.META.get('HTTP_REFERER'):
        return forbidden_redirect(request)

    doctor = request.user

    # Make sure user is a doctor
    doctor = get_object_or_404(Doctor, user=doctor)

    # Get all the codes of the centers this doctor belongs to
    doc_centers = doctor.centers.all()

    if request.method == 'POST':
        esform = ExportSelectForm(request.POST, centers=doc_centers,
                                  label_suffix='')

        if esform.is_valid():
            export_centers = doc_centers.filter(
                code__in=esform.cleaned_data.pop('export_centers'))

            csv_responses = [esform.et.export_csv(
                    obj_name, request,
                    doc_centers=export_centers,
                    sel_fields=esform.cleaned_data.get(obj_name)
                    ) for obj_name in esform.cleaned_data
                if esform.cleaned_data.get(obj_name)]

            zipped_file = esform.et.zip_files(csv_responses)
            response = HttpResponse(zipped_file,
                                    content_type='application/octet-stream')
            response['Content-Disposition'] = \
                'attachment; filename=exported.zip'

#             messages.success(
#                 request,
#                 "Επιτυχής εξαγωγή δεδομένων!")

            return response

#         else:
#             messages.error(
#                 request,
#                 "Κάποιο λάθος συνέβη κατά την εξαγωγή δεδομένων, "
#                 "παρακαλώ προσπαθήστε ξανά!")

    # Get request
    else:
        esform = ExportSelectForm(label_suffix='', centers=doc_centers)

    context = {
        'title': "Καταγραφή Ασθενών με χρόνια αναπνευστικά νοσήματα",
        'subtitle': "και χρήση αναπνευστικών συσκευών στο σπίτι",
        'esform': esform,
    }
    return render(request, 'patients/export.html', context)

@login_required
def handler_500(request):
    if not request.META.get('HTTP_REFERER'):
        return forbidden_redirect(request)

    return render(request, 'patients/errors/500.html', status=500)

@login_required
def handler_404(request):
    if not request.META.get('HTTP_REFERER'):
        return forbidden_redirect(request)

    return render(request, 'patients/errors/404.html', status=404)
