'''
Created on Jan 8, 2019

@author: b.dimitriadis
'''
import csv
import io
import zipfile

from collections import OrderedDict

from django.shortcuts import HttpResponse

from patients.models import BreathAndSleepTest, HelpAtHome
from patients.models import DeviceTestingInfo
from patients.models import ICU
from patients.models import Patient
from patients.models import PatientCharacteristics
from patients.models import PatientState
from patients.models import PatientVisit
from patients.models import PatientVentilation
import pandas as pd
# from patients.views import get_doctor_centers


# Export modules
class ExportTool:
    """ The export tool, used for any of the available tables/models the user
    might want to export
    """

    def __init__(self):
        # The obj_fields dictionary, contains the names for the the export
        # columns and corresponding field variable names, for each available
        # table (object/table name is the key for each item)
        self.obj_fields = {
            "registrations": OrderedDict([
                ("Patient_Id", "pat_id"), ("Adult", "adult"),
                ("Patient_Condition", "pat_condition__pat_condition"),
                ("Care_Center", "care_center__description"), ("ICU", "icu"),
                ("Gender", "gender__gender"), ("Birth_Year", "birth_year"),
                ("MV_Subscription_Date", "ma_subscription_date")
            ]),

            "demographics": OrderedDict([
                ("Patient_Id", "pat_id"), ("Residence", "residence"),
                ("Profession", "profession__profession"),
                ("Education", "education__education"),
                ("Caregiver_Relation", "caregiver__relation_to_patient"),
                ("Caregiver_Profession", "caregiver__profession__profession"),
                ("Caregiver_Education", "caregiver__education__education"),
                ("Comment", "comment")
            ]),

            "visits": OrderedDict([
                ("Patient_Id", "pat_id__pat_id"), ("Visit_Date", "visit_date"),
                ("Birth_Year", "pat_id__birth_year")
            ]),

            "states": OrderedDict([
                ("Patient_Id", "visit__pat_id__pat_id"),
                ("Visit Date", "visit__visit_date"),
                ("Patient_Status", "pat_status__pat_status"),
                ("Date_Of_Death", "date_of_death"),
                ("Cause_Of_Death", "cause_of_death__death_cause"),
                ("Hospitalizations_Since_Last_Visit", "hospitalizations")
            ]),

            "characteristics": OrderedDict([
                ("Patient_Id", "visit__pat_id__pat_id"),
                ("Visit_Date", "visit__visit_date"),
                ("Weight", "weight"),
                ("Height", "height"), ("Smoker", "smoker__bad_habit_status"),
                ("Alcohol", "alcohol__bad_habit_status"),
                ("Undelying_Disease", "underlying_disease__disease"),
                ("XAP", "xap"),
                ("Other_Obstructive_Disease", "other_obstructive"),
                ("Obesity_Hypoventilation", "obesity_subvent"),
                ("SAYY", "sayy"),
                ("DMD", "dmd"), ("Myasthenia", "myasthenia"), ("NKN", "nkn"),
                ("Parkinson", "parkinson"), ("Heart_failure", "heart_failure"),
                ("Other_Neurological_Disease", "other_neurological"),
                ("Diaphragm_Malfunction", "diaphragm_malfunction"),
                ("POSTTB", "posttb"), ("Kyphoscoliosis", "kyphoscoliosis"),
                ("Other_Restrictive_Lung_Disease", "other_limit_lung"),
                ("Other_Myopathy", "extra_myopathy__myopathy"),
                ("Cardiopathy", "cardiopathies__cardiopathy"),
                ("Other_Accompanying_Disease", "other_accomp__acc_disease"),
                ("SD", "sd"), ("AEE", "aee"), ("AY", "ay"),
                ("Pulmonary_Hypertension", "pulmonary_hypertension"),
                ("Nutrition", "nutrition__nutrition"),
                ("Physical_Activity", "physical_activity__physical_activity")
            ]),

            "mechanical_ventilation": OrderedDict([
                ("Patient_Id", "visit__pat_id__pat_id"),
                ("Visit_Date", "visit__visit_date"),
                ("Ventilation_Status", "ventilation_status__status"),
                ("Ventilation_Type", "ventilation_type__ventilation_type"),
                ("Ventilation_Reason", "ventilation_reason__reason"),
                ("Treatment_Provider", "treatment_provider__provider"),
                ("Support_Organization_Type",
                 "support_org_type__organization_type"),
                ("Invasive_Ventilation", "invasive_ventilation__estimation"),
                ("Tracheostomy", "tracheostomy__tracheostomy_type"),
                ("XOTH", "xoth__xoth"),
                ("XOTH_Hours_24", "xoth_hours_24"),
                ("Ventilation_Hours", "ventilation_hours"),
                ("Period_Of_Usage", "period_of_usage__period"),
                ("Application_Instructions", "application_instructions"),
                ("Physiotherapy_Instructions", "physiotherapy_instructions"),
                ("Emergency_Instructions", "emergency_instructions"),
                ("Family_Education", "family_education"),
                ("Certified_Education", "certified_education")
            ]),

            "breath_tests": OrderedDict([
                ("Patient_Id", "visit__pat_id__pat_id"),
                ("Visit_Date", "visit__visit_date"),
                ("Clinical_Symptoms", "clinical_symptoms__symptom"),
                ("Daytime_Hypercapnia", "daytime_hypercapnia"),
                ("Nocturnal_Hypoventilation", "nocturnal_hypoventilation"),
                ("Hypoxemia", "hypoxemia"),
                ("FVC (L)", "fvc_l"), ("FVC %", "fvc_perc"),
                ("FEV1 (L)", "fev1_l"), ("FEV1%", "fev_perc"),
                ("FEV1/FVC", "fev1_fvc"), ("FEF 25%-75% (L/sec)", "fev25_75"),
                ("PH", "ph"), ("PaO2 (mmHg)", "po2"),
                ("PaCO2 (mmHg)", "pco2"), ("H3CO2 (mmol/L)", "h3co2"),
                ("PINS (cmH2O)", "pins"), ("PEX (cmH2O)", "pex"),
                ("SNIP (cmH2O)", "snip"), ("PCF (L/min)", "pcf"),
                ("Overnight_Oximetry", "overnight_oximetry"),
                ("Level_Three", "level_three_rec"),
                ("Polysomnography", "polysomnography"),
                ("Capnometry", "capnometry"), ("Other", "other"),
                ("AV SaO2 Oxy", "avsao2_oxy"), ("MIN SaO2 Oxy", "minsao2_oxy"),
                ("t90 oxy", "t90_oxy"), ("ODI oxy", "odi_oxy"),
                ("AHI/RDI br", "ahirdi_br"), ("AV SaO2 br", "avsao2_br"),
                ("MIN SaO2 br", "minsao2_br"), ("t90 br", "t90_br"),
                ("ODI br", "odi_br"), ("TRT psg", "psg_trt"),
                ("TST psg", "psg_tst"), ("SL psg", "psg_sl"),
                ("SE psg", "psg_se"), ("AI psg", "psg_ai"),
                ("WASO", "waso"), ("N1 psg", "psg_n1"),
                ("N2 psg", "psg_n2"), ("N3 psg", "psg_n3"),
                ("REM psg", "psg_rem"), ("SNORE psg", "psg_snore"),
                ("AHI/RDI psg", "psg_ahirdi"), ("AV SaO2 psg", "psg_avsao2"),
                ("MIN SaO2 psg", "psg_minsao2"), ("t90 psg", "psg_t90"),
                ("ODI psg", "psg_odi"), ("Recording_Duration", "record_duration")
            ]),

            "device_info": OrderedDict([
                ("Patient_Id", "visit__pat_id__pat_id"),
                ("Visit_Date", "visit__visit_date"),
                ("MV_Type", "ma_type__type"),
                ("Device_Selection", "dev_sel__type"),
                ("Manufacturer", "manufacturer"),
                ("Serial_Number", "serial_number"),
                ("Usage_Hours", "usage_hours"), ("Humidifier", "humidifier"),
                ("Technical_Check", "technical_check"),
                ("Doctor_Informed", "doc_informed"),
                ("Mask_Type", "mask_type__type"),
                ("Check_Cause", "check_cause__cause"),
                ("Checked_By", "checked_by__by"),
                ("Additional_Info", "additional_info")
            ]),

            "help_at_home": OrderedDict([
                ("Patient_Id", "visit__pat_id__pat_id"),
                ("Visit_Date", "visit__visit_date"),
                ("Care_Place", "care_place__place"),
                ("Patient_Status", "patient_status__status"),
                ("Doctor_Visit", "doctor_visit"),
                ("Nurse_Visit", "nurse_visit"),
                ("Local_Healthcare_Provider", "local_health_care_provider"),
                ("FIAP", "fiap"),
                ("Frequent_Family_Retrain", "frequent_family_retrain"),
                ("Life_Quality_Assessment", "life_quality_assessment"),
                ("Doc_Awareness", "doc_awareness__status"),
                ("Emerging_Awareness_Cause", "emerging_awareness__status")
            ]),

            "ICU": OrderedDict([
                ("Patient_Id", "visit__pat_id__pat_id"),
                ("Visit_Date", "visit__visit_date"),
                ("Admission_From", "icu_admission_from__icu_from"),
                ("Admission_Cause", "icu_admission_cause__icu_cause"),
                ("APACHE II", "apache_II"), ("SOFA", "sofa"), ("TISS", "tiss"),
                ("GCS", "gcs"),
                ("Coexisting_Diseases",
                 "coexisting_diseases__coexisting_disease"),
                ("Stay_Duration", "icu_stay"),
                ("Complications", "complications__complication"),
                ("Patient_Outcome", "icu_outcome__outcome"),
                ("Exit_Transfer_Place", "icu_exit_transfer__transfer_place"),
                ("Death_Cause",
                 "visit__pat_state__cause_of_death__death_cause"),
                ("Death_Date", "visit__pat_state__date_of_death")
            ])
        }

    def get_doctor_centers(self, request):
        doctor = request.user

        # Get all the codes of the centers this doctor belongs to
        doc_centers = doctor.doctor.centers.all()
        return doc_centers

    def export_csv(self, obj_name, request, doc_centers=None, sel_fields=None):
        """ Get obj_name, the fields of that object to export, and the csv filename
        where those fields are going to be exported to
        """

        file_names = {"registrations": "registrations", "visits": "visits",
                      "demographics": "demographics", "states": "states",
                      "characteristics": "characteristics",
                      "mechanical_ventilation": "mechanical_ventilation",
                      "breath_tests": "breath_tests",
                      "help_at_home": "help_at_home",
                      "device_info": "device_info", "ICU": "icu"}

        objnames_objs = {
            "registrations": Patient, "visits": PatientVisit, "demographics": Patient,
            "states": PatientState, "characteristics": PatientCharacteristics,
            "mechanical_ventilation": PatientVentilation, "breath_tests": BreathAndSleepTest,
            "help_at_home": HelpAtHome, "device_info": DeviceTestingInfo,
            "ICU": ICU}

        names_fields = self.obj_fields[obj_name]

        if not sel_fields:
            sel_fields = names_fields.keys()

        field_tpls = [(name, names_fields[name]) for name in sel_fields]

        if not doc_centers:
            doc_centers = self.get_doctor_centers(request)

        return self.export_obj_csv(
            request, objnames_objs[obj_name], field_tpls,
            doc_centers, file_names[obj_name])

    def export_obj_csv(self, request, obj, field_tpls, doc_centers, filename):
        """ Export proper object and the proper fields asked by doctor.
        Each doctor can only see info of patients that belong to one of the
        doc_centers he/she is working at.
        """
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="{}.csv"'\
            .format(filename)
        response.write(u'\ufeff'.encode('utf8'))
        writer = csv.writer(response)

        field_names, fields = zip(*field_tpls)

        if obj.__name__ == 'Patient':
            objs = obj.objects.filter(
                care_centers__in=doc_centers).values_list(*fields).distinct()

        elif obj.__name__ == 'PatientVisit':
            objs = obj.objects.filter(
                pat_id__care_centers__in=doc_centers).values_list(*fields).distinct()

        else:
            objs = obj.objects.filter(
                visit__pat_id__care_centers__in=doc_centers).values_list(*fields).distinct()

        if obj.__name__ == 'BreathAndSleepTest':
            df = pd.DataFrame(objs, columns=list(field_names))
            if ("Visit_Date" in df.columns) and ("Patient_Id" in df.columns) and ("Clinical_Symptoms" in df.columns):
                dc = pd.get_dummies(df[["Patient_Id", "Visit_Date", "Clinical_Symptoms"]], columns=['Clinical_Symptoms'],
                                    drop_first=True, prefix="", prefix_sep="", dummy_na=True)
                dc.rename(columns={'nan': 'ΑΓΝΩΣΤΑ_ΣΥΜΠΤΩΜΑΤΑ'}, inplace=True)
                dc = dc.groupby(["Patient_Id", "Visit_Date"]).agg(sum)
                dc[dc >= 1] = 1
                dc = pd.merge(left=df, right=dc, left_on='Patient_Id', right_on='Patient_Id')
                dc.drop_duplicates(subset=['Patient_Id','Visit_Date'], keep='first', inplace=True)
                dc.drop('Clinical_Symptoms', axis=1, inplace=True)
                objs = list(dc.itertuples(index=False, name=None))
                field_names = dc.columns

        writer.writerow(field_names)

        for objct in objs:
            writer.writerow(objct)

        return response

    def zip_files(self, files):
        """ Zip files (i.e. csv files exported)
        """
        outfile = io.BytesIO()
        with zipfile.ZipFile(outfile, 'w') as zf:
            for f in files:
                zf.writestr(
                    f['Content-Disposition'].split("=")[-1].replace(
                        "\"", ""), f.getvalue())
        return outfile.getvalue()

# @login_required
# def export_obj_csv(request, obj, field_tpls, doc_centers, filename):
#     """ Export proper object and the proper fields asked by doctor.
#     Each doctor can only see info of patients that belong to one of the
#     doc_centers he/she is working at.
#     """
#     response = HttpResponse(content_type='text/csv')
#     response['Content-Disposition'] = 'attachment; filename="{}.csv"'\
#         .format(filename)
# 
#     writer = csv.writer(response)
# 
#     field_names, fields = zip(*field_tpls)
#     writer.writerow(field_names)
# 
#     if not doc_centers:
#         doc_centers = get_doctor_centers(request)
# 
#     if obj.__name__ == 'Patient':
#         objs = obj.objects.filter(
#             care_centers__in=doc_centers).values_list(*fields)
# 
#     elif obj.__name__ == 'PatientVisit':
#         objs = obj.objects.filter(
#             pat_id__care_centers__in=doc_centers).values_list(*fields)
# 
#     else:
#         objs = obj.objects.filter(
#             visit__pat_id__care_centers__in=doc_centers).values_list(*fields)
# 
#     for objct in objs:
#         writer.writerow(objct)
# 
#     return response
# 
# 
# @login_required
# def export_regs_csv(request, doc_centers=None, sel_fields=None):
#     """ Export only selected fields of registration info for patients belonging
#     to specific medical center/centers.
#     """
# 
#     names_fields = OrderedDict([
#         ("Patient_Id", "pat_id"), ("Adult", "adult"),
#         ("Patient_Condition", "pat_condition__pat_condition"),
#         ("Gender", "gender__gender"), ("Birth_Year", "birth_year"),
#         ("MV_Subscription_Date", "ma_subscription_date")])
# 
#     if not sel_fields:
#         sel_fields = names_fields.keys()
# 
#     field_tpls = [(name, names_fields[name]) for name in sel_fields]
# 
#     return export_obj_csv(request, Patient, field_tpls,
#                           doc_centers, "registrations")
# 
# 
# @login_required
# def export_demographics_csv(request, doc_centers=None, sel_fields=None):
#     """ Export only selected fields of demographics for patients belonging
#     to specific medical center/centers.
#     """
# 
#     names_fields = OrderedDict([
#         ("Patient_Id", "pat_id"), ("Residence", "residence"),
#         ("Profession", "profession__profession"),
#         ("Education", "education__education"),
#         ("Caregiver_Relation", "caregiver__relation_to_patient"),
#         ("Caregiver_Profession", "caregiver__profession__profession"),
#         ("Caregiver_Education", "caregiver__education__education")
#     ])
# 
#     if not sel_fields:
#         sel_fields = names_fields.keys()
# 
#     field_tpls = [(name, names_fields[name]) for name in sel_fields]
# 
#     return export_obj_csv(request, Patient, field_tpls,
#                           doc_centers, "demographics")
# 
# 
# @login_required
# def export_visits_csv(request, doc_centers=None, sel_fields=None):
#     """ Export only selected fields of visits for patients belonging
#     to specific medical center/centers.
#     """
# 
#     names_fields = OrderedDict([
#         ("Patient_Id", "pat_id__pat_id"), ("Visit_Date", "visit_date"),
#         ("Birth_Year", "pat_id__birth_year")
#     ])
# 
#     if not sel_fields:
#         sel_fields = names_fields.keys()
# 
#     field_tpls = [(name, names_fields[name]) for name in sel_fields]
# 
#     return export_obj_csv(request, PatientVisit, field_tpls,
#                           doc_centers, "visits")
# 
# 
# @login_required
# def export_states_csv(request, doc_centers=None, sel_fields=None):
#     """ Export only selected fields of state for patients belonging
#     to specific medical center/centers.
#     """
# 
#     names_fields = OrderedDict([
#         ("Patient_Id", "visit__pat_id__pat_id"),
#         ("Visit Date", "visit__visit_date"),
#         ("Patient_Status", "pat_status__pat_status"),
#         ("Date_Of_Death", "date_of_death"),
#         ("Cause_Of_Death", "cause_of_death__death_cause"),
#         ("Hospitalizations_Since_Last_Visit", "hospitalizations")
#     ])
# 
#     if not sel_fields:
#         sel_fields = names_fields.keys()
# 
#     field_tpls = [(name, names_fields[name]) for name in sel_fields]
# 
#     return export_obj_csv(request, PatientState, field_tpls,
#                           doc_centers, "states")
# 
# 
# @login_required
# def export_characteristics_csv(request, doc_centers=None, sel_fields=None):
#     """ Export only selected fields of characteristics for patients
#     belonging to specific medical center/centers.
#     """
# 
#     names_fields = OrderedDict([
#         ("Patient_Id", "visit__pat_id__pat_id"),
#         ("Visit_Date", "visit__visit_date"),
#         ("Weight", "weight"),
#         ("Height", "height"), ("Smoker", "smoker"),
#         ("Alcohol", "alcohol__bad_habit_status"),
#         ("Undelying_Disease", "underlying_disease__disease"), ("XAP", "xap"),
#         ("Other_Obstructive_Disease", "other_obstructive"),
#         ("Obesity_Hypoventilation", "obesity_subvent"), ("SAYY", "sayy"),
#         ("DMD", "dmd"), ("Myasthenia", "myasthenia"), ("NKN", "nkn"),
#         ("Parkinson", "parkinson"), ("Heart_failure", "heart_failure"),
#         ("Other_Neurological_Disease", "other_neurological"),
#         ("Diaphragm_Malfunction", "diaphragm_malfunction"),
#         ("POSTTB", "posttb"), ("Kyphoscoliosis", "kyphoscoliosis"),
#         ("Other_Restrictive_Lung_Disease", "other_limit_lung"),
#         ("Other_Myopathy", "extra_myopathy__myopathy"),
#         ("Cardiopathy", "cardiopathies__cardiopathy"),
#         ("Other_Accompanying_Disease", "other_accomp__acc_disease"),
#         ("SD", "sd"), ("AEE", "aee"), ("AY", "ay"),
#         ("Pulmonary_Hypertension", "pulmonary_hypertension"),
#         ("Nutrition", "nutrition__nutrition"),
#         ("Physical_Activity", "physical_activity__physical_activity")
#     ])
# 
#     if not sel_fields:
#         sel_fields = names_fields.keys()
# 
#     field_tpls = [(name, names_fields[name]) for name in sel_fields]
# 
#     return export_obj_csv(request, PatientCharacteristics, field_tpls,
#                           doc_centers, "characteristics")
# 
# 
# @login_required
# def export_mv_csv(request, doc_centers=None, sel_fields=None):
#     """ Export only selected fields of mechanical ventilation for patients
#     belonging to specific medical center/centers.
#     """
# 
#     names_fields = OrderedDict([
#         ("Patient_Id", "visit__pat_id__pat_id"),
#         ("Visit_Date", "visit__visit_date"),
#         ("Ventilation_Status", "ventilation_status__status"),
#         ("Ventilation_Type", "ventilation_type__ventilation_type"),
#         ("Ventilation_Reason", "ventilation_reason__reason"),
#         ("Treatment_Provider", "treatment_provider__provider"),
#         ("Support_Organization_Type", "support_org_type__organization_type"),
#         ("Clinical_Symptoms", "clinical_symptoms__symptom"),
#         ("Daytime_Hypercapnia", "daytime_hypercapnia"),
#         ("Nocturnal_Hypoventilation", "nocturnal_hypoventilation"),
#         ("Hypoxemia", "hypoxemia"),
#         ("Invasive_Ventilation", "invasive_ventilation__estimation"),
#         ("Tracheostomy", "tracheostomy__tracheostomy_type"),
#         ("XOTH", "xoth__xoth"),
#         ("XOTH_Hours_24", "xoth_hours_24"),
#         ("Ventilation_Hours", "ventilation_hours"),
#         ("Period_Of_Usage", "period_of_usage__period"),
#         ("Application_Instructions", "application_instructions"),
#         ("Physiotherapy_Instructions", "physiotherapy_instructions"),
#         ("Emergency_Instructions", "emergency_instructions"),
#         ("Family_Education", "family_education"),
#         ("Certified_Education", "certified_education")
#     ])
# 
#     if not sel_fields:
#         sel_fields = names_fields.keys()
# 
#     field_tpls = [(name, names_fields[name]) for name in sel_fields]
# 
#     return export_obj_csv(request, PatientVentilation, field_tpls,
#                           doc_centers, "mechanical_ventilation")
# 
# 
# @login_required
# def export_breath_tests_csv(request, doc_centers=None, sel_fields=None):
#     """ Export only selected fields of breath tests for patients
#     belonging to specific medical center/centers.
#     """
# 
#     names_fields = OrderedDict([
#         ("Patient_Id", "visit__pat_id__pat_id"),
#         ("Visit_Date", "visit__visit_date"),
#         ("FVC (L)", "fvc_l"), ("FVC %", "fvc_perc"),
#         ("FEV1 (L)", "fev1_l"), ("FEV1%", "fev_perc"),
#         ("FEV1/FVC", "fev1_fvc"), ("FEF 25%-75% (L/sec)", "fev25_75"),
#         ("PH", "ph"), ("PO2 (mmHg)", "po2"),
#         ("PCO2 (mmHg)", "pco2"), ("H3CO2 (mmol/L)", "h3co2"),
#         ("PINS (cmH2O)", "pins"), ("PEX (cmH2O", "pex"),
#         ("SNIF (cmH2O)", "snif"), ("PCF (L/min)", "pcf"),
#         ("Overnight_Oximetry", "overnight_oximetry"),
#         ("Level_Three", "level_three_rec"),
#         ("Polysomnography", "polysomnography"),
#         ("Capnometry", "capnometry"), ("Other", "other"),
#         ("AV SaO2 Oxy", "avsao2_oxy"), ("MIN SaO2 Oxy", "minsao2_oxy"),
#         ("t90 oxy", "t90_oxy"), ("ODI oxy", "odi_oxy"),
#         ("AHI/RDI br", "ahirdi_br"), ("AV SaO2 br", "avsao2_br"),
#         ("MIN SaO2 br", "minsao2_br"), ("t90 br", "t90_br"),
#         ("TRT psg", "psg_trt"), ("TST psg", "psg_tst"),
#         ("SL psg", "psg_sl"), ("SE psg", "psg_se"),
#         ("AI psg", "psg_ai"), ("WASO", "waso"),
#         ("N1 psg", "psg_n1"), ("N2 psg", "psg_n2"),
#         ("N3 psg", "psg_n3"), ("REM psg", "psg_rem"),
#         ("SNORE psg", "psg_snore"), ("AV SaO2 psg", "psg_avsao2"),
#         ("MIN SaO2 psg", "psg_minsao2"), ("t90 psg", "psg_t90"),
#         ("Recording_Duration", "record_duration")
#     ])
# 
#     if not sel_fields:
#         sel_fields = names_fields.keys()
# 
#     field_tpls = [(name, names_fields[name]) for name in sel_fields]
# 
#     return export_obj_csv(request, BreathAndSleepTest, field_tpls,
#                           doc_centers, "breath_tests")
# 
# 
# @login_required
# def export_dev_info_csv(request, doc_centers=None, sel_fields=None):
#     """ Export only selected fields of device tests info for patients
#     belonging to specific medical center/centers.
#     """
# 
#     names_fields = OrderedDict([
#         ("Patient_Id", "visit__pat_id__pat_id"),
#         ("Visit_Date", "visit__visit_date"),
#         ("MV_Type", "ma_type__type"), ("Device_Selection", "dev_sel__type"),
#         ("Manufacturer", "manufacturer"), ("Serial_Number", "serial_number"),
#         ("Usage_Hours", "usage_hours"), ("Humidifier", "humidifier"),
#         ("Technical_Check", "technical_check"),
#         ("Doctor_Informed", "doc_informed"), ("Mask_Type", "mask_type__type"),
#         ("Check_Cause", "check_cause__cause"),
#         ("Checked_By", "checked_by__by"),
#         ("Additional_Info", "additional_info")
#     ])
# 
#     if not sel_fields:
#         sel_fields = names_fields.keys()
# 
#     field_tpls = [(name, names_fields[name]) for name in sel_fields]
# 
#     return export_obj_csv(request, DeviceTestingInfo, field_tpls,
#                           doc_centers, "device_info")
# 
# 
# @login_required
# def export_help_at_home_csv(request, doc_centers=None, sel_fields=None):
#     """ Export only selected fields of device tests info for patients
#     belonging to specific medical center/centers.
#     """
# 
#     names_fields = OrderedDict([
#         ("Patient_Id", "visit__pat_id__pat_id"),
#         ("Visit_Date", "visit__visit_date"),
#         ("Care_Place", "care_place__place"),
#         ("Patient_Status", "patient_status__status"),
#         ("Doctor_Visit", "doctor_visit"), ("Nurse_Visit", "nurse_visit"),
#         ("Local_Healthcare_Provider", "local_health_care_provider"),
#         ("FIAP", "fiap"),
#         ("Frequent_Family_Retrain", "frequent_family_retrain"),
#         ("Life_Quality_Assessment", "life_quality_assessment"),
#         ("Doc_Awareness", "doc_awareness__status")
#     ])
# 
#     if not sel_fields:
#         sel_fields = names_fields.keys()
# 
#     field_tpls = [(name, names_fields[name]) for name in sel_fields]
# 
#     return export_obj_csv(request, HelpAtHome, field_tpls,
#                           doc_centers, "help_at_home")
# 
# 
# @login_required
# def export_icu_csv(request, doc_centers=None, sel_fields=None):
#     """ Export only selected fields of device tests info for patients
#     belonging to specific medical center/centers.
#     """
# 
#     names_fields = OrderedDict([
#         ("Patient_Id", "visit__pat_id__pat_id"),
#         ("Visit_Date", "visit__visit_date"),
#         ("Admission_From", "icu_admission_from__icu_from"),
#         ("Admission_Cause", "icu_admission_cause__icu_cause"),
#         ("APACHE II", "apache_II"), ("SOFA", "sofa"), ("TISS", "tiss"),
#         ("GCS", "gcs"),
#         ("Coexisting_Diseases", "coexisting_diseases__coexisting_disease"),
#         ("Stay_Duration", "icu_stay"),
#         ("Complications", "complications__complication"),
#         ("Patient_Outcome", "icu_outcome__outcome"),
#         ("Exit_Transfer_Place", "icu_exit_transfer__transfer_place"),
#         ("Death_Cause", "visit__pat_state__cause_of_death__death_cause"),
#         ("Death_Date", "visit__pat_state__date_of_death")
#     ])
# 
#     if not sel_fields:
#         sel_fields = names_fields.keys()
# 
#     field_tpls = [(name, names_fields[name]) for name in sel_fields]
# 
#     return export_obj_csv(request, ICU, field_tpls,
#                           doc_centers, "icu")
