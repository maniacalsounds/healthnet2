from django.test import TestCase
import datetime
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from .models import Patient,Doctor,Appointment,Nurse

# Create your tests here.

class AppointmentModelTests(TestCase):

    def setup(self):
        time1 = datetime.datetime(2016, 10, 2)
        time2 = datetime.datetime(2016, 10, 10)
        time3 = datetime.datetime(2016, 12, 3)

        Appointment.objects.create(when=time1)
        Appointment.objects.create(when=time2)
        Appointment.objects.create(when=time3)

        #Invalid Test
        #time4 = timezone.now() - datetime.timedelta(days=10)
        #Appointment.objects.create(when=time4)

    def test_all_current_appointments_for_past_dates(self):
        """
        Check the database for appointments set in the past
        """

        time = datetime.datetime(2016,10,3)

        query=Appointment.objects.all()
        if [q.when < time for q in query]:
            return False
        else:
            return True
