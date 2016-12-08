import datetime

from django import forms
from django.contrib.auth.models import User, Group
from django.db.models.sql import AND
from django.forms import widgets
from django.http import request
from django.shortcuts import redirect
from django.core.validators import EmailValidator, MaxValueValidator, MinValueValidator, RegexValidator


from log.models import Entry
from .models import Doctor, Hospital, Prescription, Patient, Appointment, Message, HealthFiles

#class RegisterTypeForm(forms.ModelForm):
    #type = forms.choi

genders = (
    ("male", "male"),
    ("female", "female"),
)
adordis = (
    ("Admit", "Admit"),
    ("Discharge", "Discharge"),
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
    #when = forms.DateTimeField(
    #      required=True,
    #      widget=DateTimePicker(options={"format": "YYYY-MM-DD HH:mm"})
    #)

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
        self.fields['when'].label = "When (YYYY-MM-DD HH:mm)"

class AdmissionForm(forms.ModelForm):
    #admission AND Discharge form
    #Note do not delete the Hospital 'None'. Using it as a default before admission
    ADorDIS = forms.ChoiceField(required=True,choices=adordis, label='Admit or Discharge')
    cur_issue = forms.CharField(max_length=300,required=True)
    hospital = forms.ModelChoiceField(queryset=Hospital.objects.all(), required=True, widget=forms.Select(attrs={'class':'selectpicker form-control', 'required': '', 'data-live-search':'true'}), empty_label="Select a Hospital")
    patient = forms.ModelChoiceField(queryset=Patient.objects.all(), required=True, widget=forms.Select(attrs={'class':'selectpicker form-control', 'required': '', 'data-live-search':'true'}), empty_label="Select a patient")


    class Meta:
        model = Patient
        fields= ('hospital','patient')

    def save(self, commit=True):
        patient = self.cleaned_data['patient']
        patient.cur_issue = self.cleaned_data['cur_issue']
        if(self.cleaned_data['ADorDIS']=='Admit'):
            patient.cur_hospital = self.cleaned_data['hospital']
            Entry.objects.createEntry(self.instance.user, 'patient Admission', datetime.datetime.now())
        if(self.cleaned_data['ADorDIS'] == 'Discharge'):
            patient.cur_hospital = Hospital.objects.get(name='None')
            Entry.objects.createEntry(self.instance.user, 'patient Discharge', datetime.datetime.now())

        patient.save()
        return patient

class TransferForm(forms.ModelForm):
    # Transfer patient form, choose hospital, choose patient, save change
    hospital = forms.ModelChoiceField(queryset=Hospital.objects.all(), required=True, widget=forms.Select(attrs={'class':'selectpicker form-control', 'required': '', 'data-live-search':'true'}), empty_label="Select a Hospital")
    ptient = forms.ModelChoiceField(queryset=Patient.objects.all(), required=True, widget=forms.Select(attrs={'class':'selectpicker form-control', 'required': '', 'data-live-search':'true'}), empty_label="Select a patient")

    class Meta:
        model = Patient
        fields= ('hospital','ptient')

    def save(self, commit=True):
        patient = self.cleaned_data['ptient']
        patient.cur_hospital = self.cleaned_data['hospital']
        patient.save()
        Entry.objects.createEntry(self.instance.user, 'patient transfer', datetime.datetime.now())
        return patient

class PrescriptionForm(forms.ModelForm):
    #compose a message to send to a user
    prescription = forms.CharField(max_length=300, required=True)
    receive = forms.ModelChoiceField(queryset=User.objects.all(), required = True, widget=forms.Select(attrs={'class':'selectpicker form-control', 'required': '', 'data-live-search':'true'}), empty_label="Select a patient")

    class Meta:
        model = Prescription
        fields = ('prescription','receive')

    def save(self, commit=True):
        prescription = Prescription.objects.create()
        prescription.receive = self.cleaned_data['receive']
        prescription.send = User.objects.get(username=self.user)
        prescription.prescription = self.cleaned_data['prescription']
        prescription.createdOn = datetime.datetime.now()
        prescription.save()
        Entry.objects.createEntry(self.user, 'Prescription prescribed', datetime.datetime.now())
        return prescription

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(PrescriptionForm, self).__init__(*args, **kwargs)


class ComposeForm(forms.ModelForm):
    #compose a message to send to a user
    msg = forms.CharField(max_length=300, required=True)
    receiver = forms.ModelChoiceField(queryset=User.objects.all(), required = True, widget=forms.Select(attrs={'class':'selectpicker form-control', 'required': '', 'data-live-search':'true'}), empty_label="Select a recipient")

    class Meta:
        model = Message
        fields = ('msg','receiver')

    def save(self, commit=True):
        message = Message.objects.create()
        message.receiver = self.cleaned_data['receiver']
        message.sender = User.objects.get(username=self.user)
        message.msg = self.cleaned_data['msg']
        message.created = datetime.datetime.now()
        message.save()
        Entry.objects.createEntry(self.user, 'message sent', datetime.datetime.now())
        return message

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.username = kwargs.pop('username', None)
        super(ComposeForm, self).__init__(*args, **kwargs)
        if self.username != '':
            userto = User.objects.get(user=self.user)
            #self.fields[receiver] = forms.ModelChoiceField(queryset=User.objects.all(), initial=userto, required = True, widget=forms.Select(attrs={'class':'selectpicker form-control', 'required': '', 'data-live-search':'true'}), empty_label="Select a recipient")
            self.fields[receiver] = 0
        #else:
        #    self.fields[receiver] = receiver = forms.ModelChoiceField(queryset=User.objects.all(), required = True, widget=forms.Select(attrs={'class':'selectpicker form-control', 'required': '', 'data-live-search':'true'}), empty_label="Select a recipient")
        #    userto = User.objects.get(user = self.user)
        #    self.fields[receiver].initial = userto



class HealthFileForm(forms.ModelForm):
    #pic = forms.ImageField(required=False)
    docfile = forms.FileField(label='Select a File', required=True)
    patient = forms.ModelChoiceField(queryset=Patient.objects.all(), required=True, widget=forms.Select(attrs={'class': 'selectpicker form-control', 'required': '', 'data-live-search': 'true'}),empty_label="Select a recipient")
    comment = forms.CharField(max_length=300, required=False)
    canview = forms.BooleanField(label='Release', required=False, initial=True)

    class Meta:
        model = HealthFiles
        fields = ('docfile','patient', 'comment', 'canview')

#    def save(self,commit=True):
 #       upload = HealthFiles.objects.create()
  #      upload.ptient = self.cleaned_data['ptient']
   #    print(self.cleaned_data['docfile'])
    #    upload.docfile = self.cleaned_data['docfile']
     #   print(upload.docfile.name)
      #  upload.save()
       # Entry.objects.createEntry(self.user, 'uploaded file', datetime.datetime.now())
        #return upload

class E_contact_createForm(forms.ModelForm):
    #Emergency_Contact_Username = forms.ModelChoiceField(queryset=Patient.objects.all(), required=False ,widget=forms.Select(attrs={'class': 'selectpicker form-control', 'required': '', 'data-live-search': 'true'}),empty_label="Select a Emergency Contact who is also a user of HealthNet")

    Emergency_Contact_Name = forms.CharField(max_length=200, required=True)
    Emergency_Contact_Address = forms.CharField(max_length=300,required=True)
    Emergency_Contact_Phone_Number = forms.CharField(max_length=12, required=True)

    class Meta:
        model = Patient
        fields = ('Emergency_Contact_Name','Emergency_Contact_Address','Emergency_Contact_Phone_Number')

    def save(self, commit=True):
        print(self.user)
        patient = Patient.objects.get(user=self.user)
        patient.E_contact_name = self.cleaned_data['Emergency_Contact_Name']
        patient.E_contact_address = self.cleaned_data['Emergency_Contact_Address']
        patient.E_contact_phoneNum = self.cleaned_data['Emergency_Contact_Phone_Number']
        patient.save()
        Entry.objects.createEntry(self.user, 'updated Emergency contact info', datetime.datetime.now())
        return patient

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(E_contact_createForm, self).__init__(*args, **kwargs)

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
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$',
                                 message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    username = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(max_length=100, label="Email", required=True, validators=[EmailValidator])
    password = forms.CharField(widget=forms.PasswordInput(), required=True)
    sex = forms.ChoiceField(choices=genders)
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=True)
    insurance_number = forms.CharField(max_length=100,required=True)
    doctor = forms.ModelChoiceField(queryset=Doctor.objects.all(), required=True)
    weight = forms.IntegerField(required=True, validators=[RegexValidator(regex=r'^\d{1,4}$',message="Must be a number between 1-4 digits.")])
    height_in_feet = forms.IntegerField(required=True, validators=[MaxValueValidator(9), MinValueValidator(1)])
    height_in_inches = forms.IntegerField(required=True, validators=[MaxValueValidator(108), MinValueValidator(12)])
    address = forms.CharField(max_length=200, validators=[RegexValidator(regex='^\d+\s[A-z]+\s[A-z]+$', message="Please enter a valid address.")])
    phone_number = forms.CharField(max_length=20, validators=[phone_regex])
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