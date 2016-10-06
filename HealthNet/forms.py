import datetime

from django import forms
from django.contrib.auth.models import User, Group
from django.db.models.sql import AND
from django.forms import widgets
from django.http import request
from django.shortcuts import redirect

from log.models import Entry
from .models import Doctor, Hospital, Patient, Appointment

#class RegisterTypeForm(forms.ModelForm):
    #type = forms.choi

genders = (
    ("male", "male"),
    ("female", "female"),
)

class DeleteAppointmentForm(forms.ModelForm):
    #patient = Patient.objects.get(user=self.user)
    when = forms.ModelChoiceField(queryset=Appointment.objects.all().order_by('when'))

    class Meta:
        model = Appointment
        fields = ('when',)

    def __init__(self, type, user, *args, **kwargs):
        super(DeleteAppointmentForm, self).__init__(*args, **kwargs)  # populates the post
        if type == 'patient':
            #They're a patient
            self.fields['when'].queryset = Appointment.objects.filter(ptient=user).order_by('when')
        elif type == 'doctor':
            self.fields['when'].queryset = Appointment.objects.filter(dr=user).order_by('when')

    #def __init__(self, user, *args, **kwargs):
    #    self.user = user
    #    super(DeleteAppointmentForm, self).__init__(*args, **kwargs)


class CreateAppointmentForm(forms.ModelForm):
    when = forms.DateTimeField()

    class Meta:
        model = Appointment
        fields = ('when',)
        exclude = ('endtime', 'dr', 'ptient')

    def save(self, commit=True):
        appointment = Appointment.objects.create()
        appointment.endtime = self.cleaned_data['when'] + datetime.timedelta(minutes=30)
        appointment.when = self.cleaned_data['when']
        patient = Patient.objects.get(user=self.user)
        appointment.ptient = patient
        appointment.dr = patient.doctor

        ##let's check for collisions
        try:
            collision = Appointment.objects.get(when__lte=appointment.endtime, endtime__gte=appointment.when, ptient=patient)
        except Appointment.DoesNotExist:
            appointment.save()
            Entry.objects.createEntry(self.user, 'appointment created', datetime.datetime.now())
            return appointment
        return redirect('calendar')

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(CreateAppointmentForm, self).__init__(*args, **kwargs)



class UpdatePatientForm(forms.ModelForm):
    #currentuser = Patient.objects.get(username=request.user.self)
    email = forms.EmailField(max_length=100, label="Email", required=True)
    sex = forms.ChoiceField(choices=genders)
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=True)
    insurance_num = forms.CharField(max_length=100, required=True, label='Insurance Number')
    doctor = forms.ModelChoiceField(queryset=Doctor.objects.all(), required=True)
    weight = forms.IntegerField(required=True)
    height_ft = forms.IntegerField(required=True, label='Height in feet')
    height_in = forms.IntegerField(required=True, label='Height in inches')
    address = forms.CharField(max_length=200)
    phone_number = forms.CharField(max_length=20)
    preferred_hospital = forms.ModelChoiceField(queryset=Hospital.objects.all(), required=True)
    #cur_hospital = forms.ModelChoiceField(queryset=Hospital.objects.all(), required=True, label='Current Hospital')

    class Meta:
        model = Patient
        fields = ('email', 'sex', 'first_name', 'last_name', 'insurance_num', 'doctor', 'weight','height_ft','height_in','address','phone_number','preferred_hospital')

class UpdateDoctorForm(forms.ModelForm):
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=True)
    address = forms.CharField(max_length=900, required=True)
    phone_number = forms.CharField(max_length=12)
    email = forms.CharField(max_length=100, required=True)
    hospital = forms.ModelChoiceField(queryset=Hospital.objects.all(),required=True)

    class Meta:
        model = Doctor
        fields = ('first_name', 'last_name', 'address', 'phone_number', 'email', 'hospital')

class PatientRegisterForm(forms.ModelForm):
    username = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(max_length=100, label="Email", required=True)
    password = forms.CharField(widget=forms.PasswordInput(), required=True)
    sex = forms.ChoiceField(choices=genders)
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=True)
    insurance_number = forms.CharField(max_length=100,required=True)
    doctor = forms.ModelChoiceField(queryset=Doctor.objects.all(), required=True)
    weight = forms.IntegerField(required=True)
    height_in_feet = forms.IntegerField(required=True)
    height_in_inches = forms.IntegerField(required=True)
    address = forms.CharField(max_length=200)
    phone_number = forms.CharField(max_length=20)
    preferred_hospital = forms.ModelChoiceField(queryset=Hospital.objects.all(), required=True)
    #current_hospital = forms.ModelChoiceField(queryset=Hospital.objects.all(), required = True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def save(self, commit=True):
        user = super(PatientRegisterForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            g, created = Group.objects.get_or_create(name="Patient")
            g.user_set.add(user)
            patient = Patient.objects.create(user=user)
            patient.user = user
            patient.doctor = self.cleaned_data['doctor']
            patient.email = self.cleaned_data['email']
            patient.sex = self.cleaned_data['sex']
            patient.first_name = self.cleaned_data['first_name']
            patient.last_name = self.cleaned_data['last_name']
            patient.insurance_num = self.cleaned_data['insurance_number']
            patient.weight = self.cleaned_data['weight']
            patient.height_ft = self.cleaned_data['height_in_feet']
            patient.height_in = self.cleaned_data['height_in_inches']
            patient.address = self.cleaned_data['address']
            patient.phone_number = self.cleaned_data['phone_number']
            #patient.preferred_hospital = Hospital.objects.get(id=self.cleaned_data['preferred_hospital'])
            patient.preferred_hospital = self.cleaned_data['preferred_hospital']
            #patient.cur_hospital = self.cleaned_data['current_hospital']
            patient.save()
            Entry.objects.createEntry(user, 'user created', datetime.datetime.now())
        return user

class AuthenticationForm(forms.Form):
    """
    Login form
    """
    username = forms.CharField(widget=forms.widgets.TextInput)
    password = forms.CharField(widget=forms.widgets.PasswordInput)

    class Meta:
        fields = ['email', 'password']