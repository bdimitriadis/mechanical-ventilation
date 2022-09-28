'''
Created on Oct 22, 2018

@author: b.dimitriadis
'''
from django.shortcuts import HttpResponse


def sorted_choices(choices_tpl):
    """ Returns choices_tpl sorted alphabetically
    """
    return sorted(choices_tpl, key=lambda el: el[1])


def str_upper(s):
    """ Strings (greek inclusive) to uppercase
    """

    gr_extra_trans = s.maketrans("ΆΈΉΊΌΎΏ", "ΑΕΗΙΟΥΩ")
    return s.upper().translate(gr_extra_trans)


def max_old_center_patient(center_code):
    """ Get the max patient id (for old patients) for specific center code
    :param center_code:
    :return the patient with the largest id from the specific center:
    """
    # The patient with the max id from each center (old patients)
    max_old_patients = ["001MV000011", "002MV000269", "003MV000013",
                        "004MV000026", "005MV000001", "006MV000013",
                        "008MV000056", "009MV000001", "010MV000073",
                        "012MV000229", "013MV000001", "014MV000008",
                        "015MV000001", "017MV000003", "019MV000005",
                        "020MV000026", "099MV000004"]

    return (list(
        filter(
            lambda p: p.startswith("{}MV".format(center_code)
                                   ), max_old_patients))+[None])[0]


def choices_max_length(tpl):
    """ Get the length of the longest (as string) choice in tpl
    """
    lst = dict(tpl).keys()
    return len(max(lst, key=len))


def authorized_centers(pat_centers, doc_centers):
    """
    Check if doctor is authorized to view or make changes for a specific patient
    :param pat_centers:
    :param doc_centers:
    :return: intersection of the two querysets, i.e. common centers
    """
    return pat_centers & doc_centers


def delete_db_rec(obj):
    """ Delete object from db
    """
    if not obj.pk:
        resp_status = 404
        resp_message = "Δυστυχώς η διαγραφή αυτή, δεν ήταν δυνατόν να "\
            "ολοκληρωθεί! Δεν υπάρχει η αντίστοιχη καταχώριση ακόμη "\
            "στο σύστημα!"
    else:
        deleted = obj.delete()
        if deleted and deleted[0]:
            resp_status = 200
            resp_message = "Η διαγραφή ολοκληρώθηκε επιτυχώς!"

        else:
            resp_status = 400
            resp_message = "Δυστυχώς η διαγραφή αυτή, δεν ήταν δυνατόν"\
                "να ολοκληρωθεί!"

    return HttpResponse(content=resp_message,
                        status=resp_status)
