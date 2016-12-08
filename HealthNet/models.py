from django.db import models
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db.models.signals import post_save
from django.utils import timezone
import datetime
from django.utils.deconstruct import deconstructible

@deconstructible
class Hospital (models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=900)
    def __str__(self):
        return str(self.name)

@deconstructible
class Doctor (models.Model):
    user = models.OneToOneField(User)
    first_name = models.CharField(max_length=100, null=True)
    last_name = models.CharField(max_length=100, null=True)
    address = models.CharField(max_length=900, null=True)
    phone_number = models.CharField(max_length=12, default=None, blank=True)
    email = models.CharField(max_length=100, default=None, blank=True)
    hospital = models.ForeignKey(Hospital, null=True)
    def __str__(self):
        return self.user.username

@deconstructible
class Patient (models.Model):
    user = models.OneToOneField(User)
    first_name = models.CharField(max_length = 100, null=True)
    last_name = models.CharField(max_length = 100, null=True)
    address = models.CharField(max_length=900, null=True)
    phone_number = models.CharField(max_length=12, blank=True)
    email = models.CharField(max_length = 100, blank=True)
    cur_issue = models.CharField(max_length = 300, blank=True)
    preferred_hospital = models.ForeignKey(Hospital, blank=True, related_name='preferred', null=True)
    cur_hospital = models.ForeignKey(Hospital, default=Hospital.objects.get(name='None'), blank=True, related_name='admitted', null=True)
    insurance_num = models.CharField(max_length = 50, blank=True)
    sex = models.CharField(max_length=6, null=True)
    E_contact = models.ForeignKey(User, blank=True, null=True, related_name='E_contactUser')
    E_contact_name = models.CharField(max_length = 100, null=True)
    E_contact_address = models.CharField(max_length =300, null =True)
    E_contact_phoneNum = models.CharField(max_length =12, null =True)
    weight = models.CharField(max_length = 10, null=True)
    height_ft = models.CharField(max_length = 3, null=True)
    height_in = models.CharField(max_length = 3, null=True)
    doctor = models.ForeignKey(Doctor, blank=True, null=True)
    def __str__(self):
        return self.user.username

@deconstructible
class Nurse (models.Model):
    user = models.OneToOneField(User)
    first_name = models.CharField(max_length=100, null=True)
    last_name = models.CharField(max_length=100, null=True)
    address = models.CharField(max_length=900, null=True)
    phone_number = models.CharField(max_length=12, blank=True)
    email = models.CharField(max_length=100, blank=True)
    hospital = models.ForeignKey(Hospital, null=True)
    def __str__(self):
        return self.user.username

@deconstructible
class Appointment(models.Model):
    when = models.DateTimeField(default=datetime.datetime.now)
    endtime = models.DateTimeField(default=datetime.datetime.now()+datetime.timedelta(minutes=30))
    dr = models.ForeignKey(Doctor, null=True, verbose_name='Doctor')
    ptient = models.ForeignKey(Patient, null=True, verbose_name='Patient')
    def __str__(self):
        return str(self.when)

    def __unicode__(self):
        return str(self.when)

@deconstructible
class Message(models.Model):
    sender = models.ForeignKey(User, null = True, related_name="sender")
    receiver = models.ForeignKey(User, null = True, related_name="reciever")
    msg = models.CharField(max_length = 300, null=True)
    created = models.DateTimeField(default=datetime.datetime.now)

    class Meta:
        verbose_name = 'Message'
    def __str__(self):
        return str(self.msg)

@deconstructible
class Prescription(models.Model):
    send = models.ForeignKey(User, null = True, related_name="send")
    receive = models.ForeignKey(User, null = True, related_name="recieve")
    prescription = models.CharField(max_length = 300, null=True)
    createdOn = models.DateTimeField(default=datetime.datetime.now)

    class Meta:
        verbose_name = 'prescription'
    def __str__(self):
        return str(self.msg)

@deconstructible

@deconstructible
class HealthFiles(models.Model):
    #picture = models.ImageField(upload_to= 'pictures')
    docfile = models.FileField(upload_to='healthnetfiles')
    patient = models.ForeignKey(Patient, null=True, verbose_name='Patient')
    doctor = models.ForeignKey(Doctor, null=True, verbose_name='Doctor')
    comment = models.CharField(max_length=300)
    canview = models.BooleanField(default=True)

    @classmethod
    def create(cls, doctor, patient, file, comment, canview):
        book = cls(doctor=doctor, patient=patient, docfile=file, comment=comment, canview=canview)
        return book


def create_patient(sender, instance, created, **kwargs):
    if created:
        Patient.objects.create(user=instance)

