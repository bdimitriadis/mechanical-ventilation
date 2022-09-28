# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class AnswerList(models.Model):
    al_id = models.AutoField(db_column='AL_ID', primary_key=True)  # Field name made lowercase.
    al_description = models.CharField(db_column='AL_DESCRIPTION', max_length=80)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'answer_list'


class BinAnswers(models.Model):
    ba_id = models.AutoField(db_column='BA_ID', primary_key=True)  # Field name made lowercase.
    ba_contact = models.ForeignKey('PatientContacts', models.DO_NOTHING, db_column='BA_CONTACT_ID')  # Field name made lowercase.
    ba_vl = models.ForeignKey('ValuesList', models.DO_NOTHING, db_column='BA_VL_ID')  # Field name made lowercase.
    ba_value = models.TextField(db_column='BA_VALUE', blank=True, null=True)  # Field name made lowercase.
    ba_target = models.CharField(db_column='BA_TARGET', max_length=7)  # Field name made lowercase.
    ba_ftype = models.CharField(db_column='BA_FTYPE', max_length=45, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'bin_answers'


class Categories(models.Model):
    c_id = models.AutoField(db_column='C_ID', primary_key=True)  # Field name made lowercase.
    c_description = models.CharField(db_column='C_DESCRIPTION', max_length=60)  # Field name made lowercase.
    c_cardinality = models.PositiveIntegerField(db_column='C_CARDINALITY')  # Field name made lowercase.
    c_priviledge = models.PositiveIntegerField(db_column='C_PRIVILEDGE')  # Field name made lowercase.
    c_order = models.IntegerField(db_column='C_ORDER')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'categories'


class ContactStatus(models.Model):
    cs_id = models.AutoField(db_column='CS_ID', primary_key=True)  # Field name made lowercase.
    cs_pc = models.ForeignKey('PatientContacts', models.DO_NOTHING, db_column='CS_PC_ID')  # Field name made lowercase.
    cs_status = models.PositiveIntegerField(db_column='CS_STATUS')  # Field name made lowercase.
    cs_date = models.DateTimeField(db_column='CS_DATE')  # Field name made lowercase.
    cs_final_date = models.DateTimeField(db_column='CS_FINAL_DATE')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'contact_status'


class Countries(models.Model):
    country_id = models.PositiveIntegerField(db_column='COUNTRY_ID', primary_key=True)  # Field name made lowercase.
    country = models.CharField(db_column='COUNTRY', max_length=20)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'countries'


class Dependencies(models.Model):
    de_id = models.AutoField(db_column='DE_ID', primary_key=True)  # Field name made lowercase.
    de_vl = models.ForeignKey('ValuesList', models.DO_NOTHING, db_column='DE_VL_ID')  # Field name made lowercase.
    de_li_vl = models.ForeignKey('ValuesList', models.DO_NOTHING, db_column='DE_LI_VL_ID')  # Field name made lowercase.
    de_ea_al = models.ForeignKey(AnswerList, models.DO_NOTHING, db_column='DE_EA_AL_ID', blank=True, null=True)  # Field name made lowercase.
    de_num_ans = models.CharField(db_column='DE_NUM_ANS', max_length=15, blank=True, null=True)  # Field name made lowercase.
    de_vl_target = models.CharField(db_column='DE_VL_TARGET', max_length=7)  # Field name made lowercase.
    de_li_vl_target = models.CharField(db_column='DE_LI_VL_TARGET', max_length=7)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'dependencies'


class EnumAnswers(models.Model):
    ea_id = models.AutoField(db_column='EA_ID', primary_key=True)  # Field name made lowercase.
    ea_contact = models.ForeignKey('PatientContacts', models.DO_NOTHING, db_column='EA_CONTACT_ID')  # Field name made lowercase.
    ea_vl = models.ForeignKey('ValuesList', models.DO_NOTHING, db_column='EA_VL_ID')  # Field name made lowercase.
    ea_value = models.ForeignKey(AnswerList, models.DO_NOTHING, db_column='EA_VALUE', blank=True, null=True)  # Field name made lowercase.
    ea_target = models.CharField(db_column='EA_TARGET', max_length=7)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'enum_answers'


class EnumConstraint(models.Model):
    ec_id = models.PositiveSmallIntegerField(db_column='EC_ID', primary_key=True)  # Field name made lowercase.
    ec_vl = models.ForeignKey('ValuesList', models.DO_NOTHING, db_column='EC_VL_ID')  # Field name made lowercase.
    ec_al = models.ForeignKey(AnswerList, models.DO_NOTHING, db_column='EC_AL_ID')  # Field name made lowercase.
    ec_al_disabled = models.IntegerField(db_column='EC_AL_DISABLED')  # Field name made lowercase.
    ec_al_order = models.PositiveIntegerField(db_column='EC_AL_ORDER', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'enum_constraint'


class NumAnswers(models.Model):
    na_contact = models.ForeignKey('PatientContacts', models.DO_NOTHING, db_column='NA_CONTACT_ID')  # Field name made lowercase.
    na_vl = models.ForeignKey('ValuesList', models.DO_NOTHING, db_column='NA_VL_ID')  # Field name made lowercase.
    na_value = models.FloatField(db_column='NA_VALUE', blank=True, null=True)  # Field name made lowercase.
    na_id = models.AutoField(db_column='NA_ID', primary_key=True)  # Field name made lowercase.
    na_target = models.CharField(db_column='NA_TARGET', max_length=7)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'num_answers'


class NumConstraint(models.Model):
    nc_vl = models.ForeignKey('ValuesList', models.DO_NOTHING, db_column='NC_VL_ID')  # Field name made lowercase.
    nc_min = models.FloatField(db_column='NC_MIN', blank=True, null=True)  # Field name made lowercase.
    nc_max = models.FloatField(db_column='NC_MAX', blank=True, null=True)  # Field name made lowercase.
    nc_id = models.PositiveSmallIntegerField(db_column='NC_ID', primary_key=True)  # Field name made lowercase.
    nc_unit = models.CharField(db_column='NC_Unit', max_length=10, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'num_constraint'


class PatientContacts(models.Model):
    pc_id = models.AutoField(db_column='PC_ID', primary_key=True)  # Field name made lowercase.
    pc_patient = models.ForeignKey('PatientsPrivate', models.DO_NOTHING, db_column='PC_PATIENT_ID')  # Field name made lowercase.
    pc_date = models.DateField(db_column='PC_DATE')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'patient_contacts'


class PatientsPrivate(models.Model):
    patient_id = models.CharField(db_column='PATIENT_ID', primary_key=True, max_length=10)  # Field name made lowercase.
    surname = models.CharField(db_column='SURNAME', max_length=30, blank=True, null=True)  # Field name made lowercase.
    forname = models.CharField(db_column='FORNAME', max_length=15, blank=True, null=True)  # Field name made lowercase.
    ppextra1 = models.CharField(db_column='PPEXTRA1', max_length=255, blank=True, null=True)  # Field name made lowercase.
    ppextra2 = models.CharField(db_column='PPEXTRA2', max_length=255, blank=True, null=True)  # Field name made lowercase.
    ppextra3 = models.CharField(db_column='PPEXTRA3', max_length=255, blank=True, null=True)  # Field name made lowercase.
    ppextra4 = models.DateField(db_column='PPEXTRA4', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'patients_private'


class TextAnswers(models.Model):
    ta_id = models.AutoField(db_column='TA_ID', primary_key=True)  # Field name made lowercase.
    ta_contact = models.ForeignKey(PatientContacts, models.DO_NOTHING, db_column='TA_CONTACT_ID')  # Field name made lowercase.
    ta_vl = models.ForeignKey('ValuesList', models.DO_NOTHING, db_column='TA_VL_ID')  # Field name made lowercase.
    text = models.TextField(db_column='TEXT', blank=True, null=True)  # Field name made lowercase.
    ta_target = models.CharField(db_column='TA_TARGET', max_length=7)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'text_answers'


class ValuesList(models.Model):
    vl_id = models.CharField(db_column='VL_ID', primary_key=True, max_length=20)  # Field name made lowercase.
    vl_caption = models.CharField(db_column='VL_CAPTION', max_length=450)  # Field name made lowercase.
    vl_category = models.ForeignKey(Categories, models.DO_NOTHING, db_column='VL_CATEGORY', blank=True, null=True)  # Field name made lowercase.
    vl_askorder = models.FloatField(db_column='VL_ASKORDER', blank=True, null=True)  # Field name made lowercase.
    vl_cardinality = models.IntegerField(db_column='VL_CARDINALITY')  # Field name made lowercase.
    vl_privilege = models.PositiveIntegerField(db_column='VL_PRIVILEGE')  # Field name made lowercase.
    vl_calculated = models.IntegerField(db_column='VL_CALCULATED')  # Field name made lowercase.
    vl_type = models.CharField(db_column='VL_TYPE', max_length=10)  # Field name made lowercase.
    vl_showspecial = models.PositiveIntegerField(db_column='VL_SHOWSPECIAL', blank=True, null=True)  # Field name made lowercase.
    vl_required = models.PositiveIntegerField(db_column='VL_REQUIRED')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'values_list'
