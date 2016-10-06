from django.db import models
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db.models.signals import post_save
from django.utils import timezone
import datetime

class Hospital (models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=900)
    def __str__(self):
        return str(self.name)

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

class Patient (models.Model):
    user = models.OneToOneField(User)
    first_name = models.CharField(max_length = 100, null=True)
    last_name = models.CharField(max_length = 100, null=True)
    address = models.CharField(max_length=900, null=True)
    phone_number = models.CharField(max_length=12, blank=True)
    email = models.CharField(max_length = 100, blank=True)
    preferred_hospital = models.ForeignKey(Hospital, blank=True, related_name='preferred', null=True)
    cur_hospital = models.ForeignKey(Hospital, blank=True, related_name='admitted', null=True)
    insurance_num = models.CharField(max_length = 50, blank=True)
    sex = models.CharField(max_length=6, null=True)
    weight = models.CharField(max_length = 10, null=True)
    height_ft = models.CharField(max_length = 3, null=True)
    height_in = models.CharField(max_length = 3, null=True)
    doctor = models.ForeignKey(Doctor, blank=True, null=True)
    def __str__(self):
        return self.user.username

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

class Appointment(models.Model):
    when = models.DateTimeField(default=datetime.datetime.now)
    endtime = models.DateTimeField(default=datetime.datetime.now()+datetime.timedelta(minutes=30))
    dr = models.ForeignKey(Doctor, null=True, verbose_name='Doctor')
    ptient = models.ForeignKey(Patient, null=True, verbose_name='Patient')
    def __str__(self):
        return str(self.when)

    def __unicode__(self):
        return str(self.when)

def create_patient(sender, instance, created, **kwargs):
    if created:
        Patient.objects.create(user=instance)