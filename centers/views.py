from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.shortcuts import HttpResponseRedirect

from centers.models import Center
from centers.models import Doctor

from centers.forms import CenterForm
from centers.forms import DoctorForm


# Create your views here.
@staff_member_required
def center_info(request,  center_id=0):
    """ The centers' info view
    """
    if center_id == 0:
        center = None
    else:
        center = get_object_or_404(Center, pk=center_id)

    if request.method == "POST":
        form = CenterForm(request.POST, instance=center, label_suffix='')
        if form.is_valid():
            form.save()
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

    else:
        form = CenterForm(instance=center, label_suffix='')

    context = {
#         'title': "Μηχανικός Αερισμός στο Σπίτι - Δεδομένα Εγγραφής",
        'title': "Μητρώο Ασθενών με χρόνια αναπνευστικά νοσήματα", #"Μηχανικός Αερισμός στο Σπίτι - Σελίδα Επίσκεψης",
        'subtitle': "και χρήση αναπνευστικών συσκευών στο σπίτι",
        'center_id': center_id,
        'form': form,
    }

    return render(request, 'centers/center_info.html', context)


@staff_member_required
def doctor_info(request, doctor_id=0):
    """ Doctors' info view
    """
    if doctor_id == 0:
        doctor = None
    else:
        doctor = get_object_or_404(Doctor, pk=doctor_id)

    if request.method == "POST":
        form = DoctorForm(request.POST, instance=doctor, label_suffix='')
        if form.is_valid():
            form.save()
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

    else:
        form = DoctorForm(instance=doctor, label_suffix='')

    context = {
#         'title': "Μηχανικός Αερισμός στο Σπίτι - Δεδομένα Εγγραφής",
        'title': "Μητρώο Ασθενών με χρόνια αναπνευστικά νοσήματα", #"Μηχανικός Αερισμός στο Σπίτι - Σελίδα Επίσκεψης",
        'subtitle': "και χρήση αναπνευστικών συσκευών στο σπίτι",
        'doctor_id': doctor_id,
        'form': form,
    }
    return render(request, 'centers/doctor_info.html', context)

