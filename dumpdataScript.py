#!/usr/bin/env python3

import os
import subprocess

tlst = [
    'auth', 'centers', 'patients.Gender', 'patients.PatientCondition',
    'patients.Education', 'patients.Profession', 'patients.BadHabit',
    'patients.PatientStatus', 'patients.DeathCause',
    'patients.UnderlyingDisease', 'patients.Cardiopathy',
    'patients.ExtraMyopathy', 'patients.ExtraAccompanyingDisease',
    'patients.Nutrition', 'patients.PhysicalActivity',
    'patients.VentilationStatus', 'patients.VentilationType',
    'patients.ClinicalSymptom', 'patients.VentilationReason',
    'patients.TreatmentProvider', 'patients.SupportOrganizationType',
    'patients.InvasiveSystemEstimation', 'patients.TracheostomyType',
    'patients.XOTH', 'patients.PeriodOfUsage', 'patients.ICUAdmissionFrom',
    'patients.ICUAdmissionCause', 'patients.CoexistingDisease',
    'patients.Complication', 'patients.ICUOutcome', 'patients.ICUExitTransfer',
    'patients.MVType', 'patients.DeviceSelection', 'patients.MaskType',
    'patients.CheckCause', 'patients.CheckedBy', 'patients.HelpAtHomeStatus',
    'patients.CarePlace', 'patients.DocAwarenessStatus',
    'patients.EmergingAwarenessStatus']

if not os.path.isdir("jsons/"):
    os.makedirs("jsons")

for el in tlst:
    #splitted = el.split()
    command_splitted = "python3 manage.py dumpdata {}".format(el).split()
    with open("jsons/{}.json".format(el), "w") as out:
        subprocess.Popen(command_splitted, stdout=out).communicate()
