from django.db import models
from django.db.models.signals import post_save
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator
from django.core.validators import MinValueValidator
from django.core.validators import RegexValidator


# Create your models here.

class Center(models.Model):
    code = models.CharField("Κωδικός κέντρου: ",
                            unique=True,
                            max_length=3,
                            validators=[RegexValidator(
                                r"\d{3}",
                                "Παράδειγμα ορθού κωδικού κέντρου: 111")]
                            )

    contact = models.ForeignKey(
        'Doctor',
        verbose_name="Επαφή επικοινωνίας: ",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Επαφή επικοινωνίας για το παρόν κέντρο",)

    phone = models.CharField(
        "Τηλέφωνο επικοινωνίας: ",
        unique=True,
        max_length=10,
        null=True,
        blank=True,
        validators=[RegexValidator(r"\d{10}",
                                   "Δεκαψήφιος αριθμός τηλεφώνου")]
        )

    description = models.TextField("Περιγραφή: ",
                                   max_length=120,
                                   default="",
                                   null=True,
                                   help_text="Περιγραφή του Κέντρου",)

    def __str__(self):
        return self.description


class Doctor(models.Model):
    user = models.OneToOneField(User, verbose_name="Ιατρός: ",
                                on_delete=models.CASCADE,
                                related_name="doctor")
    centers = models.ManyToManyField(
        Center,
        verbose_name="Κέντρα:",
        default="",
        help_text="Κέντρο ή κέντρα στα οποία δουλεύει ο συγκεκριμένος ιατρός")

    phone = models.CharField(
        "Τηλέφωνο: ",
        unique=True,
        max_length=10,
        null=True,
        blank=True,
        validators=[RegexValidator(r"\d{10}",
                                   "Δεκαψήφιος αριθμός τηλεφώνου")]
        )

    force_password_change = models.BooleanField("Εξαναγκασμένη αλλαγή κωδικού",
                                             default=True)
    def __str__(self):
        full_name = self.user.get_full_name()
        return full_name or self.user.username

@receiver(post_save, sender=User)
def create_user_profile_signal(sender, instance, created, **kwargs):
    if created:
        Doctor.objects.create(user=instance)


@receiver(pre_save, sender=User)
def password_change_signal(sender, instance, **kwargs):
    try:
        user = User.objects.get(username=instance.username)
        if user.password != instance.password:
            doctor = user.doctor
            doctor.force_password_change = False
            doctor.save()
    except User.DoesNotExist:
        pass
