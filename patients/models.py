from datetime import datetime
from decimal import Decimal

# from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator
from django.core.validators import MinValueValidator
from django.db import models

from centers.models import Center

from patients.validators import pat_id_validator
from patients.validators import prof_validator
from patients.validators import sn_validator
# from patients.helper_modules import sorted_choices
from patients.validators import address_validator
from patients.helper_modules import choices_max_length


# Create your models here.

class Gender(models.Model):
    """ Patient's gender choice
    """

    gender_choices = [("ΑΝΔΡΑΣ", "Άνδρας"),
                      ("ΓΥΝΑΙΚΑ", "Γυναίκα"),
                      ("ΑΛΛΟ", "Άλλο"),
                      ("ΑΓΝΩΣΤΟ", "Δεν επιθυμώ να δηλώσω")]

    gender = models.CharField(
        "Φύλο: ",
        unique=True,
        max_length=choices_max_length(gender_choices),
        choices=gender_choices,
        default=None,)

    def __str__(self):
        return dict(self.gender_choices)[self.gender]

    class Meta:
        ordering = ['id',]


class PatientCondition(models.Model):
    """ Patient's condition, concerning the medical intervention used
    i.e. Ventilation System, Tracheostomy, Sleep Apnea Syndrome etc.
    """

    condition_choices = (("ΤΡΑΧΕΙΟΣΤΟΜΙΑ", "Τραχειοστομία"),
                         ("ΣΑΥΥ", "Συνδρομο Απνοιών - Υποπνοιών Ύπνου"),
                         ("ΜΗΧΑΝΙΚΟΣ ΑΕΡΙΣΜΟΣ", "Μηχανικός Αερισμός"),)

    #  Condition choices should appear in alphabetical order
    # condition_choices = sorted_choices(condition_choices)

    pat_condition = models.CharField("Κατάσταση Ασθενούς: ",
                                     unique=True,
                                     max_length=choices_max_length(
                                         condition_choices),
                                     choices=condition_choices,
                                     default=None)

    def __str__(self):
        return dict(self.condition_choices)[self.pat_condition]


class Education(models.Model):
    """ Patient's level of education
    """
    edu_choices = (("ΑΓΝΩΣΤΟ", "Άγνωστο"),
                   ("ΑΝΑΛΦΑΒΗΤΟΣ", "Αναλφάβητος"),
                   ("ΑΝΩΤΑΤΗ ΕΚΠΑΙΔΕΥΣΗ", "Ανώτατη Εκπαίδευση"),
                   ("ΑΝΩΤΕΡΗ ΕΚΠΑΙΔΕΥΣΗ", "Ανώτερη Εκπαίδευση"),
                   ("ΒΑΣΙΚΗ ΕΚΠΑΙΔΕΥΣΗ", "Βασική Εκπαίδευση"),
                   ("ΜΕΣΗ ΕΚΠΑΙΔΕΥΣΗ", "Μέση Εκπαίδευση"),)

    #  Education choices should appear in alphabetical order
    # edu_choices = sorted_choices(edu_choices)

    education = models.CharField("Επίπεδο Μόρφωσης: ",
                                 unique=True,
                                 default=None,
                                 max_length=choices_max_length(edu_choices),
                                 choices=edu_choices,)

    def __str__(self):
        return dict(self.edu_choices)[self.education]


class Profession(models.Model):
    """ Patient's profession
    """

    prof_choices = (
        ("ΦΟΙΤΗΤΗΣ-ΣΠΟΥΔΑΣΤΗΣ", "Φοιτητής-Σπουδαστής"),
        ("ΟΙΚΙΑΚΑ", "Οικιακά"),
        ("ΣΥΝΤΑΞΙΟΥΧΟΣ", "Συνταξιούχος"),
        ("ΕΛΕΥΘΕΡΟΣ ΕΠΑΓΓΕΛΜΑΤΙΑΣ", "Ελεύθερος Επαγγελματίας"),
        ("ΔΗΜΟΣΙΟΣ ΥΠΑΛΛΗΛΟΣ", "Δημόσιος Υπάλληλος"),
        ("ΙΔΙΩΤΙΚΟΣ ΥΠΑΛΛΗΛΟΣ", "Ιδιωτικός Υπάλληλος"),
        ("ΕΠΑΓΓΕΛΜΑΤΙΑΣ ΟΔΗΓΟΣ", "Επαγγελματίας Οδηγός"),
        ("ΑΝΕΡΓΟΣ", "Άνεργος"),)

    profession = models.CharField(max_length=choices_max_length(prof_choices),
                                  unique=True,
                                  default=None,
                                  choices=prof_choices,
                                  validators=[prof_validator],)

    def __str__(self):
        return dict(self.prof_choices)[self.profession]

    class Meta:
        ordering = ['profession']


class Caregiver(models.Model):
    """ Info about the patient's caregiver,
    concerning profession, education and relation to the patient
    """
    profession = models.ForeignKey(
        Profession,
        on_delete=models.PROTECT,
        null=True,
        help_text="Το επάγγελμα του φροντιστή του ασθενούς",)

    education = models.ForeignKey(
        Education,
        on_delete=models.PROTECT,
        null=True,
        help_text="Το μορφωτικό επίπεδο του φροντιστή του ασθενούς",)

    relation_choices = (("ΜΗΤΕΡΑ", "Μητέρα"),
                        ("ΠΑΤΕΡΑΣ", "Πατέρας"),
                        ("ΑΛΛΟ", "Άλλο"),)


    relation_to_patient = models.CharField("Φροντιστής: ",
                                           max_length=choices_max_length(
                                               relation_choices),
                                           choices=relation_choices,
                                           default="")

    unique_together = (('profession', 'education', 'relation_to_patient'),)


def current_year():
    return datetime.now().year


def max_value_current_year(value):
    return MaxValueValidator(current_year())(value)


class Patient(models.Model):
    """Patient Info
    """

    # Patient's Registration data section fields
    pat_id = models.CharField(
        "Αναγνωριστικό Ατόμου: ",
        unique=True,
        max_length=11,
        validators=[pat_id_validator],
        help_text="Το ειδικό αναγνωριστικό/κωδικός του ασθενούς",)

    gender = models.ForeignKey(Gender,
                               null=True,
                               on_delete=models.PROTECT,)

    adultery_choices = ((True, 'Ενήλικας'), (False, 'Παιδί'))
    adult = models.BooleanField('Ηλικιακή Κατηγορία: ',
                                choices=adultery_choices,
                                default=True)

    pat_condition = models.ForeignKey(
        PatientCondition,
        null=True,
        on_delete=models.PROTECT,)

    care_center = models.ForeignKey(
        Center,
        null=True,
        on_delete=models.PROTECT,
        related_name='care_center',
        verbose_name='Κέντρο Περίθαλψης/Παρακολούθησης: ',
        help_text="Το κέντρο περίθαλψης/παρακολούθησης του ασθενούς, στην "
                  "παρούσα χρονική περίοδο ή το κέντρο στο οποίο θα μεταβεί.")

    care_centers = models.ManyToManyField(
        Center,
        related_name='care_centers',
        help_text="Τα κέντρα περίθαλψης/παρακολούθησης από τα οποία έχει "
                  "περάσει ο ασθενής ")

    icu = models.BooleanField("ΜΕΘ", default=False)

    birth_year = models.PositiveSmallIntegerField('Έτος Γεννήσεως',
                                                  null=True,
                                                  validators=[MinValueValidator(1900),
                                                              max_value_current_year])

    ma_subscription_date = models.DateField(null=True,)

    # Patient Demographics Section Fields
    residence = models.CharField("Κατοικία: ",
                                 max_length=60,
                                 null=True,
                                 default="",
                                 validators=[address_validator],
                                 help_text="Στην περίπτωση χωριού συμπληρώνεται Νομός, "
                                           "στην περίπτωση πόλης συμπληρώνεται όνομα πόλης",)

    profession = models.ForeignKey(Profession,
                                   on_delete=models.PROTECT,
                                   null=True,
                                   help_text="Επάγγελμα ασθενούς",)

    education = models.ForeignKey(Education,
                                  null=True,
                                  on_delete=models.PROTECT,
                                  help_text="Επίπεδο μόρφωσης ασθενούς",)

    caregiver = models.ForeignKey(
        Caregiver,
        null=True,
        default=None,
        on_delete=models.SET_NULL,)

    comment = models.TextField("Σχόλιο: ",
                               max_length=120,
                               default="",
                               null=True,
                               blank=True,
                               help_text="Σύντομο σχόλιο έως 120 χαρακτήρες",)

    def get_age(self):
        return datetime.now().year - self.birth_year


class BadHabit(models.Model):
    bh_choices = (("ΝΑΙ", "Ναι"),
                  ("ΟΧΙ", "Όχι"),
                  ("ΠΡΩΗΝ", "Πρώην"),)

    bad_habit_status = models.CharField(choices=bh_choices,
                                        max_length=choices_max_length(
                                            bh_choices))

    def __str__(self):
        return dict(self.bh_choices)[self.bad_habit_status]


class PatientVisit(models.Model):
    """ Visits per patient
    """
    pat_id = models.ForeignKey(Patient, on_delete=models.CASCADE)
    visit_date = models.DateField()

    class Meta:
        # Primary key, combination of pat_id and visit_date
        unique_together = (('pat_id', 'visit_date'),)


class PatientStatus(models.Model):
    """ Patient's state, at the time of a specific visit
    """
    status_choices = (("ΒΕΛΤΙΩΣΗ", "Βελτίωση"),
                      ("ΣΤΑΘΕΡΗ ΚΑΤΑΣΤΑΣΗ", "Σταθερή Κατάσταση"),
                      ("ΕΠΙΔΕΙΝΩΣΗ", "Επιδείνωση"),
                      ("ΘΑΝΑΤΟΣ", "Θάνατος"),
                      ("ΔΙΑΚΟΠΗ ΠΑΡΑΚΟΛΟΥΘΗΣΗΣ", "Διακοπή Παρακολούθησης"),)

    pat_status = models.CharField("Έκβαση Ασθενούς: ",
                                  max_length=choices_max_length(
                                      status_choices),
                                  default=None,)

    def __str__(self):
        return dict(self.status_choices)[self.pat_status]


class DeathCause(models.Model):
    """ Possible causes of death
    """
    death_cause_choices = (
        ("ΑΝΑΠΝΕΥΣΤΙΚΑ ΑΙΤΙΑ",
            "Αναπνευστικά Αίτια"),
        ("ΜΗ ΑΝΑΠΝΕΥΣΤΙΚΑ ΑΙΤΙΑ",
            "Μη αναπνευστικά αίτια"),
        ("ΑΓΝΩΣΤΟ", "Άγνωστο"),)

    death_cause = models.CharField("Αιτία Θανάτου:",
                                   max_length=choices_max_length(
                                       death_cause_choices),
                                   default=None,)

    def __str__(self):
        return dict(self.death_cause_choices)[self.death_cause]


class PatientState(models.Model):
    """ Patient's state
    """

    visit = models.OneToOneField(
        PatientVisit, related_name='pat_state', on_delete=models.CASCADE)

    # Patient's status
    pat_status = models.ForeignKey(PatientStatus,
                                   verbose_name="Έκβαση ασθενούς: ",
                                   null=True,
                                   on_delete=models.PROTECT)

    # Shown in form, only if patient is dead
    date_of_death = models.DateField("Ημερομηνία Θανάτου: ", null=True)

    cause_of_death = models.ForeignKey(DeathCause,
                                       verbose_name="Αιτία Θανάτου: ",
                                       on_delete=models.PROTECT,
                                       null=True)

    hospitalizations = models.\
        PositiveSmallIntegerField(
            "Νοσηλείες: ",
            null=True,
            default=None,
            help_text="Αριθμός νοσηλειών από την προηγούμενη καταγραφή")


class UnderlyingDisease(models.Model):
    """ Possible underlying diseases
    """
    disease_choices = (("ΑΠΟΦΡΑΚΤΙΚΟΥ ΤΥΠΟΥ", "Αποφρακτικού Τύπου"),
                       ("ΠΕΡΙΟΡΙΣΤΙΚΟΥ ΤΥΠΟΥ", "Περιοριστικού Τύπου"),
                       ("ΜΙΚΤΗ ΠΝΕΥΜΟΝΟΠΑΘΕΙΑ", "Μικτή Πνευμονοπάθεια"),
                       ("ΑΛΛΟ", "Άλλο"),)

    disease = models.CharField("Βασική Πάθηση: ",
                               max_length=choices_max_length(
                                   disease_choices),
                               choices=disease_choices,
                               default=None,)

    def __str__(self):
        return dict(self.disease_choices)[self.disease]


class Cardiopathy(models.Model):
    """ Possible cardiopathies
    """
    cardiopathies_choices = (
        ("ΣΝ", "ΣΝ"), ("ΑΡΡΥΘΜΙΑ", "Αρρυθμία"),
        ("ΒΑΛΒΙΔΟΠΑΘΕΙΑ", "Βαλβιδοπάθεια"),
        ("ΔΚΑ", "ΔΚΑ"), ("ΑΚΑ", "ΑΚΑ"), )

    cardiopathy = models.CharField("Καρδιοπάθεια: ",
                                   max_length=choices_max_length(
                                       cardiopathies_choices),
                                   choices=cardiopathies_choices,
                                   default=None)

    def __str__(self):
        return dict(self.cardiopathies_choices)[self.cardiopathy]

    class Meta:
        ordering = ['cardiopathy']


class ExtraMyopathy(models.Model):
    """ Other possible myopathies
    """
    extra_myopathy_choices = (
        ("SMA", "SMA"),
        ("ΕΓΚΕΦΑΛΟΠΑΘΕΙΑ", "Εγκεφαλοπάθεια"),
        ("ΜΕΤΑΒΟΛΙΚΑ ΝΟΣΗΜΑΤΑ", "Μεταβολικά Νοσήματα"),
        ("ΚΥΣΤΙΚΗ ΙΝΩΣΗ", "Κυστική Ίνωση"),
        ("ΑΛΛΟ", "Άλλο"),
        )

    myopathy = models.CharField("Άλλη Μυοπάθεια: ",
                                max_length=choices_max_length(
                                    extra_myopathy_choices),
                                choices=extra_myopathy_choices,
                                default=None)

    def __str__(self):
        return dict(self.extra_myopathy_choices)[self.myopathy]


class ExtraAccompanyingDisease(models.Model):
    """ Other possible accompanying diseases
    """
    extra_accompanying_choices = (("ΑΝΟΣΟΑΝΕΠΑΡΚΕΙΑ", "Ανοσοανεπάρκεια"),
                                  ("ΡΕΥΜΑΤΙΚΑ ΝΟΣΗΜΑΤΑ", "Ρευματικά Νοσήματα"),
                                  ("ΓΟΠ", "ΓΟΠ"),
                                  ("ΧΡΟΝΙΟ ΜΗ ΑΝΑΠΝΕΥΣΤΙΚΟ ΝΟΣΗΜΑ",
                                   "Χρόνιο Μη Αναπνευστικό Νόσημα"))

    acc_disease = models.CharField("Άλλο: ",
                                   max_length=choices_max_length(
                                       extra_accompanying_choices),
                                   choices=extra_accompanying_choices,
                                   default=None)

    def __str__(self):
        return dict(self.extra_accompanying_choices)[self.acc_disease]


class Nutrition(models.Model):
    """ Nutrition info about the patient
    """
    nutr_choices = (("ΦΥΣΙΚΗ", "Φυσική"),
                    ("ΡΙΝΟΓΑΣΤΡΙΚΟΣ ΣΩΛΗΝΑΣ", "Ρινογαστρικό Σωλήνας"),
                    ("ΓΑΣΤΡΟΣΤΟΜΙΑ", "Γαστροστομία"),
                    ("ΠΑΡΕΝΤΕΡΙΚΗ", "Παρεντερική"),)

    nutrition = models.CharField("Διατροφή",
                                 max_length=choices_max_length(nutr_choices),
                                 choices=nutr_choices)

    def __str__(self):
        return dict(self.nutr_choices)[self.nutrition]


class PhysicalActivity(models.Model):
    """ Physical Activity info about the patient
    """
    physical_activity_choices = (("ΦΥΣΙΟΛΟΓΙΚΗ", "Φυσιολογική"),
                                 ("ΠΕΡΙΟΡΙΣΜΕΝΗ ΑΛΛΑ ΕΞΥΠΗΡΕΤΕΙΤΑΙ",
                                  "Περιορισμένη αλλά εξυπηρετείται"),
                                 ("ΔΕΝ ΕΞΥΠΗΡΕΤΕΙΤΑΙ", "Δεν εξυπηρετείται"),
                                 ("ΚΛΙΝΗΡΗΣ", "Κλινήρης"),
                                 ("ΑΛΛΟ", "Άλλο"),)

    physical_activity = models.CharField("Φυσική Δραστηριότητα: ",
                                         max_length=choices_max_length(
                                             physical_activity_choices),
                                         choices=physical_activity_choices)

    def __str__(self):
        return dict(self.physical_activity_choices)[self.physical_activity]


class PatientCharacteristics(models.Model):
    """ Patient's characteristics. Conclusions about a patient's health
    condition (progress or aggrevation) could possibly be extracted, by
    studying the changes (if any) on those characteristics from visit to visit.
    """

    visit = models.OneToOneField(
        PatientVisit, related_name='pat_chars', on_delete=models.CASCADE)

    # General Characteristics
    weight = models.PositiveSmallIntegerField("Βάρος (kg): ",
                                              validators=[
                                                  MaxValueValidator(700),
                                                  MinValueValidator(0)
                                                  ])

    height = models.PositiveSmallIntegerField("Ύψος (cm): ", validators=[
            MaxValueValidator(400),
            MinValueValidator(0)
        ])

    smoker = models.ForeignKey(BadHabit, verbose_name="Κάπνισμα: ",
                               on_delete=models.PROTECT, related_name='smoker',
                               null=True)

    alcohol = models.ForeignKey(BadHabit, verbose_name="Αλκοόλ: ",
                                on_delete=models.PROTECT,
                                related_name='alcohol',
                                null=True)

    underlying_disease = models.ForeignKey(UnderlyingDisease,
                                           verbose_name="Βασική Πάθηση: ",
                                           default=None,
                                           on_delete=models.PROTECT)

    # Disease Specification
    dis_spec_labels = ["ΧΑΠ", "Άλλη Αποφρακτική Νόσος",
                       "Παχυσαρκία-Υποαερισμός", "ΣΑΥΥ", "DMD",
                       "Μυασθένεια", "NKN", "Parkinson", "Καρδιακή Ανεπάρκεια",
                       "Άλλη Νευρολογική Νόσος", "Δυσλειτουργία Διαφράγματος",
                       "POSTTB", "Κυφοσκολίωση",
                       "Άλλη Περιοριστική Πνευμονοπάθεια"]

    # Checkbox fields created in a more dynamic way
    xap, other_obstructive, obesity_subvent, sayy, dmd, myasthenia, nkn,\
        parkinson, heart_failure, other_neurological, diaphragm_malfunction,\
        posttb, kyphoscoliosis, other_limit_lung = [
            models.BooleanField(lbl, default=False)
            for lbl in dis_spec_labels]

    extra_myopathy = models.ForeignKey(ExtraMyopathy,
                                       verbose_name="Άλλη Μυοπάθεια: ",
                                       null=True,
                                       blank=True,
                                       default=None,
                                       on_delete=models.PROTECT)

    # Accompanying diseases
    cardiopathies = models.ForeignKey(Cardiopathy,
                                      verbose_name="Καρδιοπάθεια: ",
                                      null=True,
                                      blank=True,
                                      default=None,
                                      on_delete=models.PROTECT)

    acc_dis_labels = ["ΣΔ", "ΑΕΕ", "ΑΥ",
                      "Πνευμονική Υπέρταση"]

    other_accomp = models.ManyToManyField(ExtraAccompanyingDisease,
                                          verbose_name="Άλλο: ",
                                          blank=True)

    # Checkbox fields created in a more dynamic way
    sd, aee, ay, pulmonary_hypertension = [
        models.BooleanField(lbl, default=False)
        for lbl in acc_dis_labels]

    # Additional Info
    nutrition = models.ForeignKey(Nutrition,
                                  verbose_name="Διατροφή: ",
                                  on_delete=models.PROTECT)

    physical_activity = models.ForeignKey(
        PhysicalActivity,
        verbose_name="Φυσική Δραστηριότητα: ",
        null=True,
        on_delete=models.PROTECT)


class VentilationStatus(models.Model):
    """ Ventilation's usage status, during visit
    """
    status_choices = (("ΕΝΑΡΞΗ ΕΦΑΡΜΟΓΗΣ", "Έναρξη Εφαρμογής"),
                      ("ΑΛΛΑΓΗ ΤΥΠΟΥ ΜΑ", "Αλλαγή Τύπου ΜΑ"),
                      ("ΑΛΛΑΓΗ ΣΥΣΚΕΥΗΣ", "Αλλαγή Συσκευής"),
                      ("ΔΙΑΚΟΠΗ ΜΑ", "Διακοπή ΜΑ"),
                      ("ΤΑΚΤΙΚΟ ΡΑΝΤΕΒΟΥ", "Τακτικό Ραντεβού"),)

    status = models.CharField("Κατάσταση - καταγραφή λόγω:",
                              max_length=choices_max_length(status_choices),
                              choices=status_choices)

    def __str__(self):
        return dict(self.status_choices)[self.status]


class VentilationType(models.Model):
    """ Ventilation type
    """
    type_choices = (("ΕΠΕΜΒΑΤΙΚΟΣ", 'Επεμβατικός'),
                    ("ΜΗ ΕΠΕΜΒΑΤΙΚΟΣ", 'Μη επεμβατικός'))

    ventilation_type = models.CharField("Τύπος ΜΑ: ",
                                        max_length=choices_max_length(
                                            type_choices),
                                        choices=type_choices)

    def __str__(self):
        return dict(self.type_choices)[self.ventilation_type]


class ClinicalSymptom(models.Model):
    """ Clinical symptoms
    """
    symptom_choices = (("ΔΥΣΠΝΟΙΑ", "Δύσπνοια"), ("ΥΠΝΗΛΙΑ", "Υπνηλία"),
                       ("ΑΫΠΝΙΑ", "Αϋπνία"), ("ΡΟΧΑΛΗΤΟ", "Ροχαλητό"),
                       ("ΚΟΠΩΣΗ", "Κόπωση"))

    symptom = models.CharField("Κλινικά συμπτώματα: ",
                               max_length=choices_max_length(
                                   symptom_choices),
                               choices=symptom_choices)

    def __str__(self):
        return dict(self.symptom_choices)[self.symptom]


class VentilationReason(models.Model):
    """ Reason for ventilation system usage
    """
    reason_choices = [(el, el) for el in ["ΟΑΑ", "ΧΑΑ", "ΑΛΛΟ"]]

    reason = models.CharField("Λόγω: ",
                              max_length=choices_max_length(reason_choices),
                              choices=reason_choices)

    def __str__(self):
        return dict(self.reason_choices)[self.reason]


class TreatmentProvider(models.Model):
    """ Treatment (concerning the ventilation system support), is provided to
    patient by either a clinic or an icu
    """
    provider_choices = (("ΜΕΘ", "ΜΕΘ"),
                        ("ΚΛΙΝΙΚΗ", "Κλινική"), )

    provider = models.CharField(
        "Από: ",
        max_length=choices_max_length(provider_choices),
        choices=provider_choices)

    def __str__(self):
        return dict(self.provider_choices)[self.provider]


class SupportOrganizationType(models.Model):
    """ The clinic or icu supporting the patient, can be either public or private
    """
    organization_type_choices = (("ΙΔΙΩΤΙΚΟΣ", "Ιδιωτικός"),
                                 ("ΔΗΜΟΣΙΟΣ", "Δημόσιος"), )

    organization_type = models.CharField(
        "Φορέας: ",
        max_length=choices_max_length(
            organization_type_choices),
        choices=organization_type_choices)

    def __str__(self):
        return dict(self.organization_type_choices)[self.organization_type]


class InvasiveSystemEstimation(models.Model):
    """ Estimation of system effectiveness
    """
    estimation_choices = (
        ("ΑΔΥΝΑΜΙΑ ΑΠΟΔΕΣΜΕΥΣΗΣ", "Αδυναμία Αποδέσμευσης"),
        ("ΑΠΟΤΥΧΙΑ ΜΗΕΜΑ", "Αποτυχία ΜηΕΜΑ"),
        ("ΑΔΥΝΑΜΙΑ ΔΙΑΧΕΙΡΙΣΗΣ ΕΚΚΡΙΣΕΩΝ", "Αδυναμία Διαχείρισης Εκκρίσεων"),
        ("ΑΛΛΟ", "Άλλο"),
        )

    estimation = models.CharField(
        "Επεμβατικός ΜΑ: ",
        max_length=choices_max_length(estimation_choices),
        choices=estimation_choices)

    def __str__(self):
        return dict(self.estimation_choices)[self.estimation]


class TracheostomyType(models.Model):
    """ Tracheostomy types (cuff/cuffless)
    """
    type_choices = (
        ("CUFF", "Cuff"),
        ("CUFFLESS", "Cuffless"),
        )

    tracheostomy_type = models.CharField(
        "Τραχειοστομία: ",
        max_length=choices_max_length(type_choices),
        choices=type_choices)

    def __str__(self):
        return dict(self.type_choices)[self.tracheostomy_type]


class XOTH(models.Model):
    """ ΧΟΘ choices
    """

    xoth_choices = (
        ("ΜΑ+ΗΜΕΡΑ", "MA+Ημέρα"),
        ("ΜΟΝΟ ΜΕ ΜΑ", "Μόνο με ΜΑ"),
        ("ΟΧΙ", "Όχι"), ("ΔΙΑΚΟΠΗ", "Διακοπή")
        )

    xoth = models.CharField(
        "ΧΟΘ: ",
        max_length=choices_max_length(xoth_choices),
        choices=xoth_choices)

    def __str__(self):
        return dict(self.xoth_choices)[self.xoth]


class PeriodOfUsage(models.Model):
    """ Periods of use, concerning ventilation system
    """
    period_choices = (
        ("ΝΥΧΤΕΡΙΝΗ", "Νυχτερινή"),
        ("ΝΥΧΤΕΡΙΝΗ+ΗΜΕΡΗΣΙΑ", "Νυχτερινή και Ημερήσια"),
        ("ΣΥΝΕΧΗΣ", "Συνεχής"),
        )

    period = models.CharField(
        "Χρονική περίοδος χρήσης ΜΑ: ",
        max_length=choices_max_length(period_choices),
        choices=period_choices)

    def __str__(self):
        return dict(self.period_choices)[self.period]


class PatientVentilation(models.Model):
    """ Patient's ventilation system info
    """

    visit = models.OneToOneField(
        PatientVisit, related_name='pat_vent', on_delete=models.CASCADE)

    # Ventilation system's status, on specific visit
    ventilation_status = models.ForeignKey(
        VentilationStatus,
        verbose_name="Κατάσταση - καταγραφή λόγω: ",
        default=None,
        on_delete=models.PROTECT)

    # Ventilation type (surgery/non-surgery)
    ventilation_type = models.ForeignKey(VentilationType,
                                         verbose_name="Τύπος ΜΑ: ",
                                         default="",
                                         on_delete=models.PROTECT)

    # Reason for ventilation usage
    ventilation_reason = models.ForeignKey(VentilationReason,
                                           verbose_name="Λόγω: ",
                                           default=None,
                                           on_delete=models.PROTECT,
                                           )

    # Ventilation system treatment provider
    treatment_provider = models.ForeignKey(
        TreatmentProvider,
        verbose_name="Από: ",
        default="",
        on_delete=models.PROTECT,
        help_text="Φορέας Χορήγησης του συστήματος ΜΑ")

    # Field showing whether the ventilation system treatment provider belongs
    # to public or private sector
    support_org_type = models.ForeignKey(
        SupportOrganizationType,
        verbose_name="Φορέας: ",
        default="",
        on_delete=models.PROTECT,
        help_text="Τύπος του φορέα χορήγησης του συστήματος ΜΑ")

    invasive_ventilation = models.ForeignKey(
        InvasiveSystemEstimation,
        verbose_name="Επεμβατικός ΜΑ: ",
        default=None,
        null=True,
        on_delete=models.PROTECT
        )

    tracheostomy = models.ForeignKey(
        TracheostomyType,
        verbose_name="Τραχειοστομία: ",
        default=None,
        null=True,
        on_delete=models.PROTECT
        )

    xoth = models.ForeignKey(
        XOTH,
        verbose_name="ΧΟΘ: ",
        default=None,
        null=True,
        on_delete=models.PROTECT
        )

    xoth_hours_24 = models.PositiveSmallIntegerField("Ώρες 24ωρο ΧΟΘ: ",
                                                     default=None,
                                                     null=True,
                                                     validators=[
                                                         MaxValueValidator(24),
                                                         MinValueValidator(0)
                                                     ])

    ventilation_hours = models.PositiveIntegerField("Ώρες χρήσης ΜΑ: ",
                                                    default=None,
                                                    null=True,
                                                    validators=[
                                                        MinValueValidator(0)
                                                    ])

    period_of_usage = models.ForeignKey(
        PeriodOfUsage,
        verbose_name="Χρονική περίοδος χρήσης ΜΑ: ",
        default=None,
        null=True,
        on_delete=models.PROTECT
        )

    # Some of the ventilation home usage field labels
    home_usage_labels = [
        "Γραπτές Οδηγίες Εφαρμογής", "Γραπτές Οδηγίες Φυσικοθεραπείας",
        "Γραπτές Οδηγίες Αντιμετώπισης Επείγοντος", "Εκπαίδευση Οικογένειας",
        "Πιστοποιημένο Πρόγραμμα Εκπαίδευσης"]

    # Checkbox fields created in a more dynamic way
    application_instructions, physiotherapy_instructions,\
        emergency_instructions, family_education,\
        certified_education = [
            models.BooleanField(lbl, default=False)
            for lbl in home_usage_labels]


class ICUAdmissionFrom(models.Model):
    """ The place where the patient received treatment, before the ICU
    """
    icu_from_choices = (
        ("ΤΕΠ", "ΤΕΠ"),
        ("ΚΛΙΝΙΚΗ", "Κλινική"),
        ("ΧΕΙΡΟΥΡΓΕΙΟ", "Χειρουργείο"),
        ("ΑΛΛΟ ΝΟΣΟΚΟΜΕΙΟ", "Άλλο Νοσοκομείο"),
        ("ΣΠΙΤΙ", "Σπίτι"),
        )

    icu_from = models.CharField(
        "Εισαγωγή από: ",
        max_length=choices_max_length(icu_from_choices),
        choices=icu_from_choices)

    def __str__(self):
        return dict(self.icu_from_choices)[self.icu_from]


class ICUAdmissionCause(models.Model):
    """ The reason why the patient was transfered to ICU
    """
    icu_cause_choices = (
        ("ΧΕΙΡΟΥΡΓΙΚΗ", "Χειρουργική"),
        ("ΑΝΑΠΝΕΥΣΤΙΚΗ ΝΟΣΟΣ", "Αναπνευστική Νόσος"),
        ("ΝΕΥΡΟΛΟΓΙΚΗ ΝΟΣΟΣ", "Νευρολογική Νόσος"),
        ("ΚΑΡΔΙΑΓΓΕΙΑΚΗ", "Καρδιαγγειακή"),
        ("ΓΑΣΤΡΕΝΤΕΡΙΚΗ", "Γαστρεντερική"),
        ("ΝΕΦΡΟΛΟΓΙΚΗ", "Νεφρολογική"),
        ("ΤΡΑΥΜΑ", "Τραύμα"),
        ("ΣΗΠΤΙΚΗ ΣΥΝΔΡΟΜΗ", "Σηπτική Συνδρομή"),
        )

    icu_cause = models.CharField(
        "Αιτία εισαγωγής: ",
        max_length=choices_max_length(icu_cause_choices),
        choices=icu_cause_choices)

    def __str__(self):
        return dict(self.icu_cause_choices)[self.icu_cause]


class CoexistingDisease(models.Model):
    """ Coexisting diseases
    """
    disease_choices = (
        ("ΚΑΡΔΙΑΚΗ ΑΝΕΠΑΡΚΕΙΑ", "Καρδιακή Ανεπάρκεια"),
        ("ΧΑΠ", "ΧΑΠ"),
        ("ΝΕΦΡΙΚΗ ΑΝΕΠΑΡΚΕΙΑ", "Νεφρική Ανεπάρκεια"),
        ("AIDS", "AIDS"),
        ("ΚΑΡΚΙΝΟΣ", "Καρκίνος"),
        ("ΝΕΥΡΟΜΥΙΚΗ ΝΟΣΟΣ", "Νευρομυϊκή Νόσος"),
        ("ΑΛΛΟ", "Άλλο"),
        )

    coexisting_disease = models.CharField(
        "Συνυπάρχουσες παθήσεις: ",
        max_length=choices_max_length(disease_choices),
        choices=disease_choices)

    def __str__(self):
        return dict(self.disease_choices)[self.coexisting_disease]


class Complication(models.Model):
    """ Any sort of possible complications
    """
    complication_choices = (
        ("ΜΥΟΠΑΘΕΙΑ", "Μυοπάθεια"),
        ("ΚΑΤΑΚΛΙΣΕΙΣ", "Κατακλίσεις"),
        ("ΝΟΣΟΚΟΜΕΙΑΚΗ ΛΟΙΜΩΞΗ", "Νοσοκομειακή Λοίμωξη"),
        ("ΣΗΨΗ", "Σήψη"),
        ("ΠΝΕΥΜΟΝΙΚΗ ΕΜΒΟΛΗ", "Πνευμονική Εμβολή"),
        ("DELIRIUM", "Delirium"),
        )

    complication = models.CharField(
        "Επιπλοκές: ",
        max_length=choices_max_length(complication_choices),
        choices=complication_choices)

    def __str__(self):
        return dict(self.complication_choices)[self.complication]


class ICUOutcome(models.Model):
    """ ICU treatment's outcome on patient
    """
    outcome_choices = (
        ("ΕΞΟΔΟΣ", "Έξοδος"),
        ("ΘΑΝΑΤΟΣ", "Θάνατος"),
        )

    outcome = models.CharField(
        "Έκβαση: ",
        max_length=choices_max_length(outcome_choices),
        choices=outcome_choices)

    def __str__(self):
        return dict(self.outcome_choices)[self.outcome]


class ICUExitTransfer(models.Model):
    """ Place where the patient is transfered, in case he/she exits ICU
    """
    transfer_choices = (
        ("ΝΟΣΟΚΟΜΕΙΟ", "Νοσοκομείο"),
        ("ΙΔΡΥΜΑ ΑΠΟΚΑΤΑΣΤΑΣΗΣ", "Ίδρυμα Αποκατάστασης"),
        ("ΣΠΙΤΙ", "Σπίτι"),
        )

    transfer_place = models.CharField(
        "Μεταφορά λόγω εξόδου σε: ",
        max_length=choices_max_length(transfer_choices),
        choices=transfer_choices,
        help_text="Τόπος μεταφοράς του ασθενούς λόγω εξόδου από τη ΜΕΘ")

    def __str__(self):
        return dict(self.transfer_choices)[self.transfer_place]


class ICU(models.Model):
    """ Case of ICU
    """
    visit = models.OneToOneField(
        PatientVisit, related_name='pat_icu', on_delete=models.CASCADE)

    # ICU section
    icu_admission_from = models.ForeignKey(
        ICUAdmissionFrom,
        verbose_name="Εισαγωγή από: ",
        default=None,
        on_delete=models.PROTECT
        )

    icu_admission_cause = models.ForeignKey(
        ICUAdmissionCause,
        verbose_name="Αιτία Εισαγωγής: ",
        default=None,
        on_delete=models.PROTECT
        )

    # Disease severity (scoring system)
    severity_labels_limits = [
        ("APACHE II", [0, 71]), ("SOFA", [0, 70]),
        ("TISS", [0, 70])]

    # Indicator integer fields created in a more dynamic way
    apache_II, sofa, tiss = [
            models.PositiveSmallIntegerField(
                "{}: ".format(lbl),
                default=None,
                null=True,
                blank=True,
                validators=[MinValueValidator(lims[0]),
                            MaxValueValidator(lims[1])]
                )
            for lbl, lims in severity_labels_limits]

    gcs = models.PositiveSmallIntegerField(
                "GCS",
                default=None,
                null=True,
                blank=False,
                validators=[MinValueValidator(3),
                            MaxValueValidator(15)]
                )

    coexisting_diseases = models.ManyToManyField(
        CoexistingDisease,
        verbose_name="Συνυπάρχουσες παθήσεις: ",
        default=None,
        )

    icu_stay = models.PositiveSmallIntegerField(
                "Διάρκεια παραμονής ΜΕΘ",
                default=None,
                validators=[MinValueValidator(0),
                            MaxValueValidator(200)]
                )

    complications = models.ManyToManyField(
        Complication,
        verbose_name="Επιπλοκές: ",
        default=None,
        )

    icu_outcome = models.ForeignKey(
        ICUOutcome,
        verbose_name="Έκβαση: ",
        default=None,
        on_delete=models.PROTECT
        )

    icu_exit_transfer = models.ForeignKey(
        ICUExitTransfer,
        verbose_name="Μεταφορά σε: ",
        null=True,
        default=None,
        on_delete=models.PROTECT
        )


class BreathAndSleepTest(models.Model):
    """ Patient's breathing tests
    """
    visit = models.OneToOneField(
        PatientVisit, related_name='pat_breath_test', on_delete=models.CASCADE)

    # Some of the estimation fields' labels
    vent_est_labels = ["Ημερήσια Υπερκαπνία", "Νυχτερινό Υποαερισμό",
                       "Υποξαιμία"]

    clinical_symptoms = models.ManyToManyField(
        ClinicalSymptom,
        verbose_name="Κλινικά Συμπτώματα: ",
        default=None)

    # Checkbox fields created in a more dynamic way
    daytime_hypercapnia,\
        nocturnal_hypoventilation, hypoxemia = [
            models.BooleanField(lbl, default=False)
            for lbl in vent_est_labels]

    # The indicators' labels and decimal value limits for breath tests
    # Third value in each tuple is decimal digits number
    labels_limits = [
        ("FVC (L)", [0.0, 5.0], 1), ("FVC %", [0.0, 150.0], 1),
        ("FEV1 (L)", [0.0, 5.0], 1), ("FEV1%", [0.0, 150.0], 1),
        ("FEV1/FVC", [0.0, 150.0], 1), ("FEF 25%-75%", [0.0, 5.0], 1),
        ("PH", [0, 7.9], 2), ("PaO2 (mmHg)", [0.0, 100.0], 1),
        ("PaCO2 (mmHg)", [0.0, 100.0], 1), ("H3CO2 (mmol/L)", [0.0, 50.0], 1),
        ("PINS (cmH2O)", [0.0, 150.0], 1), ("PEX (cmH2O)", [0.0, 150.0], 1),
        ("SNIP (cmH2O)", [0.0, 150.0], 1), ("PCF (L/min)", [0.0, 600.0], 1)]

    # Indicator decimal fields created in a more dynamic way
    fvc_l, fvc_perc, fev1_l, fev_perc, fev1_fvc, fev25_75, ph, po2, pco2,\
        h3co2, pins, pex, snip, pcf = [
            models.DecimalField(
                "{}: ".format(lbl),
                decimal_places=dec,
                max_digits=4,
                validators=[MinValueValidator(Decimal(str(lims[0]))),
                            MaxValueValidator(Decimal(str(lims[1])))]
                )
            for lbl, lims, dec in labels_limits]

    # Some of the sleep tests' field labels
    sleeping_test_labels = [
        "Νυχτερινή Οξυμετρία", "Καταγραφή Τύπου ΙΙΙ",
        "Πολυπνογραφία", "Καπνομετρία",
        "Άλλο"]

    # Checkbox fields created in a more dynamic way
    overnight_oximetry, level_three_rec, polysomnography,\
        capnometry, other = [
            models.BooleanField(lbl, default=False)
            for lbl in sleeping_test_labels]

    # The indicators' labels and integer value limits for sleep tests
    # Third value in each tuple is decimal digits number
    oxymetry_labels_limits = [
        ("AV SaO2", [0.0, 100.0], 1), ("MIN SaO2", [0.0, 100.0], 1),
        ("t90", [0.0, 100.0], 1), ("ODI", [0.0, 100.0], 1)]

    breath_labels_limits = [
        ("AHI/RDI", [0.0, 100.0], 1), ("AV SaO2", [0.0, 100.0], 1),
        ("MIN SaO2", [0.0, 100.0], 1), ("t90", [0.0, 100.0], 1),
        ("ODI", [0.0, 100.0], 1)]

    # If dec is 0 (3rd element in tuple) shows decimal places
    psg_labels_limits = [
        ("TRT", [0, 600], 0), ("TST", [0, 600], 0),
        ("SL", [0, 600], 0), ("SE", [0.0, 100.0], 2),
        ("AI", [0.0, 100.0], 1), ("WASO", [0, 600], 0),
        ("N1", [0.0, 100.0], 1), ("N2", [0.0, 100.0], 1),
        ("N3", [0.0, 100.0], 1), ("REM", [0.0, 100.0], 1),
        ("SNORE", [0.0, 100.0], 1), ("AHI/RDI", [0.0, 100.0], 1),
        ("AV SaO2", [0.0, 100.0], 1), ("MIN SaO2", [0.0, 100.0], 1),
        ("t90", [0.0, 100.0], 1), ("ODI", [0.0, 100.0], 1)]

    record_duration = models.PositiveIntegerField(
        "Διάρκεια Καταγραφής",
        default=None,
        null=True,
        validators=[MinValueValidator(4)])

    # Indicator integer fields created in a more dynamic way
    avsao2_oxy, minsao2_oxy, t90_oxy, odi_oxy,\
        ahirdi_br, avsao2_br, minsao2_br, t90_br, odi_br, psg_trt, \
        psg_tst, psg_sl, psg_se, psg_ai, waso, psg_n1, psg_n2, psg_n3, \
        psg_rem, psg_snore, psg_ahirdi, psg_avsao2, psg_minsao2, psg_t90, \
        psg_odi = [
            models.DecimalField(
                "{}: ".format(lbl),
                decimal_places=dec,
                max_digits=4,
                default=None,
                null=True,
                validators=[MinValueValidator(Decimal(str(lims[0]))),
                            MaxValueValidator(Decimal(str(lims[1])))]
                )
            if dec > 0 else models.PositiveSmallIntegerField(
                "{}: ".format(lbl),
                default=None,
                null=True,
                validators=[MinValueValidator(lims[0]),
                            MaxValueValidator(lims[1])],
                help_text="Ο δείκτης αυτός συμπληρώνεται σε λεπτά (min)"
                )
            for lbl, lims, dec
            in oxymetry_labels_limits+breath_labels_limits+psg_labels_limits
            ]


class MVType(models.Model):
    """ Type of mechanical ventilation system
    """
    type_choices = (
        ("ΜΗ ΕΜΑ", "ΜηΕΜΑ"),
        ("ΕΜΑ", "ΕΜΑ"),
        )

    type = models.CharField(
        "Τύπος ΜΑ: ",
        max_length=choices_max_length(type_choices),
        choices=type_choices)

    def __str__(self):
        return dict(self.type_choices)[self.type]


class DeviceSelection(models.Model):
    """ Specification of the supporting device used
    """
    type_choices = (
        ("CPAP", "CPAP"),
        ("AUTO CPAP", "Auto CPAP"),
        ("BPAPS", "BPAPS"),
        ("BPAPS/T", "BPAPS/T"),
        ("BPAPAVAPS", "BPAPAVAPS"),
        ("ΑΝΑΠΝΕΥΣΤΗΡΑΣ ΠΙΕΣΗΣ", "Αναπνευστήρας Πίεσης"),
        ("ΑΝΑΠΝΕΥΣΤΗΡΑΣ ΟΓΚΟΥ", "Αναπνευστήρας Όγκου"),
        ("iVAPs", "iVAPs"),
        ("ΑΝΑΠΝΕΥΣΤΗΡΑΣ ΠΙΕΣΗΣ-ΟΓΚΟΥ", "Αναπνευστήρας Πίεσης-Όγκου"),
        )

    type = models.CharField(
        "Επιλογή Συσκευής Υποστήριξης: ",
        max_length=choices_max_length(type_choices),
        choices=type_choices)

    def __str__(self):
        return dict(self.type_choices)[self.type]


class MaskType(models.Model):
    """ Type of mask used
    """
    type_choices = (
        ("ΡΙΝΙΚΗ", "Ρινική"),
        ("ΡΙΝΟΣΤΟΜΑΤΙΚΗ", "Ρινοστοματική"),
        ("ΟΛΟΠΡΟΣΩΠΙΚΗ", "Ολοπροσωπική"),
        ("ΣΥΝΔΥΑΣΜΟΣ", "Συνδυασμός"),
        )

    type = models.CharField(
        "Μάσκα: ",
        max_length=choices_max_length(type_choices),
        choices=type_choices)

    def __str__(self):
        return dict(self.type_choices)[self.type]


class CheckCause(models.Model):
    """ Reason, why the device is checked. Could reveal check frequency.
    """
    cause_choices = (
        ("ΣΥΣΤΗΜΑΤΙΚΑ", "Συστηματικά"),
        ("ΚΑΤΑ ΠΕΡΙΠΤΩΣΗ", "Κατά περίπτωση"),
        ("ΑΙΤΗΜΑ ΙΑΤΡΟΥ", "Αίτημα ιατρού"),
        ("ΑΙΤΗΜΑ ΑΣΘΕΝΟΥΣ", "Αίτημα ασθενούς"),
        )

    cause = models.CharField(
        "Τεχνικός Έλεγος Συσκευής ΜΑ: ",
        max_length=choices_max_length(cause_choices),
        choices=cause_choices)

    def __str__(self):
        return dict(self.cause_choices)[self.cause]


class CheckedBy(models.Model):
    """ Shows who checked/tested the device
    """
    by_choices = (
        ("ΦΟΡΕΑ", "Φορέα"),
        ("ΠΡΟΜΗΘΕΥΤΗ", "Προμηθευτή"),
        ("ΑΛΛΟ", "Άλλο"),
        )

    by = models.CharField(
        "Τεχνικός Έλεγος Συσκευής ΜΑ: ",
        max_length=choices_max_length(by_choices),
        choices=by_choices)

    def __str__(self):
        return dict(self.by_choices)[self.by]


class DeviceTestingInfo(models.Model):
    """ Various Info about device tests carried out (or not)
    """
    visit = models.OneToOneField(
        PatientVisit, related_name='pat_dev_test', on_delete=models.CASCADE)

    ma_type = models.ForeignKey(MVType,
                                verbose_name="Τύπος ΜΑ: ",
                                default=None,
                                on_delete=models.PROTECT)

    dev_sel = models.ForeignKey(DeviceSelection,
                                verbose_name="Επιλογή Συσκευής Υποστήριξης: ",
                                default=None,
                                on_delete=models.PROTECT)

    manufacturer = models.CharField(
        "Κατασκευαστής Συσκευής: ",
        blank=True,
        max_length=30,
        )

    serial_number = models.CharField(
        "Serial Number: ",
        max_length=30,
        blank=True,
        validators=[sn_validator],
        help_text=" Ο σειριακός αριθμός της συσκευής"
        )

    usage_hours = models.PositiveIntegerField(
        "Ώρες Χρήσης στη Συσκευή: ",
        default=None,
        help_text="Οι ώρες χρήσης που αναγράφονται στη συσκευή")

    # Create boolean fields in a more automatic way
    labels = ["Υγραντήρας", "Γίνεται Τεχνικός Έλεγχος",
              "Αποτελέσματα Τεχνικού Ελέγχου / Ενημέρωση Υπεύθυνου Γιατρού"]

    humidifier, technical_check, doc_informed = [
            models.BooleanField(lbl, default=False)
            for lbl in labels]

    mask_type = models.ForeignKey(MaskType,
                                  verbose_name="Μάσκα: ",
                                  null=True,
                                  default=None,
                                  on_delete=models.PROTECT)

    check_cause = models.ForeignKey(
        CheckCause,
        verbose_name="Τεχνικός Έλεγχος Συσκευής ΜΑ: ",
        default=None,
        null=True,
        on_delete=models.PROTECT,
        help_text="Αιτία (ένδειξη συχνότητας) ελέγχου της συσκευής")

    checked_by = models.ForeignKey(
        CheckedBy,
        verbose_name="Τεχνικός Έλεγχος Από: ",
        default=None,
        null=True,
        on_delete=models.PROTECT,
        help_text="Από ποιόν πραγματοποιήθηκε ο έλεγχος της συσκευής")

    additional_info = models.CharField(
        "Συμπληρωματικά Στοιχεία Συσκευής: ",
        max_length=30,
        blank=True,
        help_text="Πιθανές χρήσιμες πρόσθετες πληροφορίες για τη συσκευή"
        )


class CarePlace(models.Model):
    """ Care provider: care provider at  home or clinic
    """
    place_choices = (
        ("ΦΡΟΝΤΙΔΑ ΣΤΟ ΣΠΙΤΙ", "Φροντίδα στο σπίτι"),
        ("ΦΡΟΝΤΙΔΑ ΣΤΟ ΙΔΡΥΜΑ", "Φροντίδα στο ίδρυμα"),
        )

    place = models.CharField(
        "Είδος Φροντίδας: ",
        max_length=choices_max_length(place_choices),
        choices=place_choices)

    def __str__(self):
        return dict(self.place_choices)[self.place]


class HelpAtHomeStatus(models.Model):
    """ Status of patient as far as help at home is concerned
    """
    status_choices = (
        ("ΑΥΤΟΕΞΥΠΗΡΕΤΟΥΜΕΝΟΣ", "Αυτοεξυπηρετούμενος"),
        ("ΜΕΡΙΚΩΣ ΕΞΑΡΤΗΜΕΝΟΣ", "Μερικώς Εξαρτημένος"),
        ("ΠΛΗΡΩΣ ΕΞΑΡΤΗΜΕΝΟΣ", "Πλήρως Εξαρτημένος"),
        )

    status = models.CharField(
        "Κατάσταση ασθενούς: ",
        max_length=choices_max_length(status_choices),
        choices=status_choices)

    def __str__(self):
        return dict(self.status_choices)[self.status]


class DocAwarenessStatus(models.Model):
    """ Status showing the doctor's awareness of the patient's condition
    """
    status_choices = (
        ("TAKTIKH ΕΝΗΜΕΡΩΣΗ", "Τακτική Ενημέρωση"),
        ("EKTAKTH ΕΝΗΜΕΡΩΣΗ", "Έκτακτη Ενημέρωση"),
        ("ΔΕΝ ΥΠΑΡΧΕΙ ΕΝΗΜΕΡΩΣΗ", "Δεν Υπάρχει Ενημέρωση"),
        )

    status = models.CharField(
        "Διασύνδεση ασθενούς με κλινική παρακολούθησης: ",
        max_length=choices_max_length(status_choices),
        choices=status_choices)

    def __str__(self):
        return dict(self.status_choices)[self.status]


class EmergingAwarenessStatus(models.Model):
    """ Status specification, showing the doctor's awareness of the patient's
    condition in emergency cases
    """
    status_choices = (
        ("ΑΝΑΦΟΡΑ ΕΠΕΙΓΟΝΤΟΣ", "Αναφορά Επείγοντος"),
        ("ΕΙΣΑΓΩΓΗ ΣΕ ΑΛΛΗ ΚΛΙΝΙΚΗ", "Εισαγωγή σε Άλλη Κλινική"),
        ("ΒΛΑΒΗ - ΛΕΙΤΟΥΡΓΙΚΟ ΠΡΟΒΛΗΜΑ ΣΥΣΚΕΥΗΣ",
         "Βλάβη / Λειτουργικό Πρόβλημα Συσκευής"),
        )

    status = models.CharField(
        "Έκτακτη ενημέρωση: ",
        max_length=choices_max_length(status_choices),
        choices=status_choices)

    def __str__(self):
        return dict(self.status_choices)[self.status]


class HelpAtHome(models.Model):
    """ Help at home info
    """
    visit = models.OneToOneField(
        PatientVisit, related_name='pat_help_at_home',
        on_delete=models.CASCADE)

    care_place = models.ForeignKey(
        CarePlace,
        verbose_name="Είδος φροντίδας: ",
        default="",
        on_delete=models.PROTECT
        )

    patient_status = models.ForeignKey(
        HelpAtHomeStatus,
        verbose_name="Κατάσταση ασθενούς: ",
        default=None,
        on_delete=models.PROTECT,
        help_text="Κατάσταση του ασθενούς / βαθμός ανάγκης βοήθειας-υποστήριξης")

    # Create boolean fields in a more automatic way
    labels = [
        "Επίσκεψη Γιατρού", "Επίσκεψη Νοσηλευτή",
        "Σύνδεση με Τοπικό Φορέα Υγείας", "Σύνδεση με ΦΙΑΠ",
        "Περιοδική Μετεκπαίδευση Οικογένειας", "Εκτίμηση Ποιότητας Ζωής"]

    doctor_visit, nurse_visit, local_health_care_provider,\
        fiap, frequent_family_retrain, life_quality_assessment = [
            models.BooleanField(lbl, default=False)
            for lbl in labels]

    doc_awareness = models.ForeignKey(
        DocAwarenessStatus,
        verbose_name="Διασύνδεση ασθενούς με κλινική παρακολούθησης: ",
        default=None,
        on_delete=models.PROTECT,
        help_text="Ενημέρωση του κέντρου παροχής/χορήγησης μηχανικού αερισμού "
                  "και παρακολούθησης, από τον αρμόδιο γιατρό, τον ασθενή "
                  "ή την οικογένειά του")

    emerging_awareness = models.ForeignKey(
        EmergingAwarenessStatus,
        verbose_name="Έκτακτη ενημέρωση: ",
        default=None,
        null=True,
        on_delete=models.PROTECT,
        help_text="Υποδεικνύει το περιεχόμενο/λόγο της έκτακτης ενημέρωσης "
                  "του κέντρου")
