
# Create your views here.
from collections import OrderedDict

from django.contrib.auth.decorators import login_required
#from django.core.serializers import json
import json as json
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect, render
from django.template import RequestContext, context
from django.contrib.auth import login as django_login, authenticate, logout as django_logout
from django.http import HttpResponseRedirect
from django.templatetags.tz import localtime

from django.db.models import Count, Avg

from log.models import Entry
from json.encoder import i

from .forms import PatientRegisterForm, AuthenticationForm, HealthFileForm, UpdatePatientForm, UpdateDoctorForm, CreateAppointmentForm, \
    DeleteAppointmentForm, E_contact_createForm, ComposeForm, PrescriptionForm, TransferForm, AdmissionForm
from datetime import date
from .models import Appointment, Prescription, Patient, Doctor, Message, HealthFiles, User, Hospital
import datetime
from calendar import monthrange

###

def date_handler(obj):
    """
    Handles JSON serialization for datetime values
    """
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    else:
        raise TypeError(
            "Unserializable object {} of type {}".format(obj, type(obj))
        )


def convert_field_names(event_list):
    """
    Converts atribute names from Python code convention to the
    attribute names used by FullCalendar
    """
    for event in event_list:
        for key in event.keys():
            event[snake_to_camel_case(key)] = event.pop(key)
    return event_list


def snake_to_camel_case(s):
    """
    Converts strings from 'snake_case' (Python code convention)
    to CamelCase
    """
    new_string = s

    leading_count = 0
    while new_string.find('_') == 0:
        new_string = new_string[1:]
        leading_count += 1

    trailing_count = 0
    while new_string.rfind('_') == len(new_string) - 1:
        new_string = new_string[:-1]
        trailing_count += 1

    new_string = ''.join([word.title() for word in new_string.split('_')])
    leading_underscores = '_' * leading_count
    trailing_underscores = '_' * trailing_count
    return leading_underscores + new_string[0].lower() + new_string[1:] + trailing_underscores


def events_to_json(events_queryset):
    """
    Dumps a CalendarEvent queryset to the JSON expected by FullCalendar
    """
    events_values = list(events_queryset.values('id', 'ptient', 'when', 'endtime'))
    events_values = convert_field_names(events_values)
    return json.dumps(events_values, default=date_handler)


def calendar_options(event_url, options):
    """
    Builds the Fullcalendar options array
    This function receives two strings. event_url is the url that returns a JSON array containing
    the calendar events. options is a JSON string with all the other options.
    """
    event_url_option = 'events: "%s"' % (event_url,)
    s = options.strip()
    if s is not None and '{' in s:
        pos = s.index('{') + 1
    else:
        return '{%s}' % (event_url_option)
    return s[:pos] + event_url_option + ', ' + s[pos:]

###

def login(request):
    """
    Log in view
    """

    #redirect if user is already logged in.
    if request.user.is_authenticated():
        return redirect('/dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = authenticate(username=request.POST['username'], password=request.POST['password'])
            if user is not None:
                if user.is_active:
                    django_login(request,user)
                    Entry.objects.createEntry(user, 'user login', datetime.datetime.now())
                    return redirect('dashboard')
            else:
                return redirect('badlogin.html')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


def register(request):
    """
    User registration view.
    """

    # redirect if user is already logged in.
    if request.user.is_authenticated():
        return redirect('/dashboard')

    if request.method == 'POST':
        form = PatientRegisterForm(data=request.POST)
        if form.is_valid():
            user = form.save()
            return redirect('/dashboard')
    else:
        form = PatientRegisterForm()
    return render(request, 'register.html',{'form': form})

@login_required
def admission(request):
    if request.user.is_superuser:
        return redirect('/dashboard')

    #must be doctor or nurse will add nurse soon
    try:
        instance = Doctor.objects.get(user=request.user)
        type = 'Doctor'
    except Doctor.DoesNotExist:
        return redirect('/dashboard')

    if type == 'Doctor':
        form = AdmissionForm(request.POST, instance=instance)
    if form.is_valid():
        form.save()
        return redirect('/dashboard')

    return render(request, 'admission.html',{'form':form})

@login_required
def transfer(request):
    if request.user.is_superuser:
        return redirect('/dashboard')

    #must be doctor or admin will add admin soon
    try:
        instance = Doctor.objects.get(user=request.user)
        type = 'Doctor'
    except Doctor.DoesNotExist:
        return redirect('/dashboard')

    if type == 'Doctor':
        form = TransferForm(request.POST, instance=instance)
    if form.is_valid():
        form.save()
        return redirect('/dashboard')

    return render(request, 'transfer.html',{'form':form})

@login_required
def E_contact_view(request):
    if request.user.is_superuser:
        return redirect('/dashboard')

    PatientUser = Patient.objects.get(user=request.user)
    return render_to_response('E_contact_view.html',{'PatientUser':PatientUser}, context_instance=RequestContext(request))

@login_required
def E_contact_create_View(request):
    if request.user.is_superuser:
        return redirect('/dashboard')

    try:
        instance = Patient.objects.get(user=request.user)
        type = 'patient'
    except Patient.DoesNotExist:
        type = 'else'

    if type == 'patient':
        form = E_contact_createForm(request.POST or None, instance=instance, user=request.user)
    elif type == 'else':
        return redirect('/dashboard')

    if form.is_valid():
        form.save()
        return redirect('/dashboard')

    return render(request, 'E_contact_create.html',{'form': form})

@login_required
def update(request):
    """
    User registration view.
    """
    if request.user.is_superuser:
        return redirect('/dashboard')

    try:
        instance = Patient.objects.get(user=request.user)
        type = 'patient'
    except Patient.DoesNotExist:
        instance = Doctor.objects.get(user=request.user)
        type = 'doctor'

    if type == 'patient':
        form = UpdatePatientForm(request.POST or None, instance=instance)
    elif type == 'doctor':
        form = UpdateDoctorForm(request.POST or None, instance=instance)
    if form.is_valid():
        form.save()
        return redirect('/dashboard')

    return render(request, 'update.html',{'form': form})

@login_required
def logout(request):
    """
    Log out view
    """
    Entry.objects.createEntry(request.user, 'user logout', datetime.datetime.now())
    django_logout(request)
    return redirect('/')

def named_month(month_number):
    """
    Return the name of the month, given the number.
    """
    return date(1900, month_number, 1).strftime("%B")

def this_month(request):
    """
    Show calendar of events this month.
    """
    today = datetime.datetime.now()
    return calendar(request, today.year, today.month)

@login_required
def prescriptionView(request):
    # base message viewer

    if request.user.is_superuser:
        return redirect('/dashboard')

    received = Prescription.objects.filter(receive=request.user).order_by('-createdOn')
    try:
        doctor = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        doctor = None

    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        patient = None

    if doctor != None:
        sent = Prescription.objects.filter(send=request.user).order_by('-createdOn')
    else:
        sent = None

    if patient != None:
        type = None
    else:
        type= 'Doctor'
    return render_to_response('prescriptionView.html',{'received': received, 'sent': sent, 'type':type}, context_instance=RequestContext(request))


@login_required
def deletePrescription(request, id):
    #simply deletes the prescription object selected

    if request.user.is_superuser:
        return redirect('/dashboard')

    Prescription.objects.filter(id=id).delete()
    return render(request, 'deletePrescription.html')

@login_required
def createPrescription(request):
    #creates the message using the compose form

    if request.user.is_superuser:
        return redirect('/dashboard')

    if request.method == 'POST':
        form = PrescriptionForm(data=request.POST, user=request.user)
        if form.is_valid():
            form.save()
            Entry.objects.createEntry(request.user, 'prescription prescribed', datetime.datetime.now())
            return redirect('/prescriptionView')
    else:
        form = PrescriptionForm(user=request.user)
    return render(request, 'createPrescription.html',{'form': form},)


@login_required
def Messenger(request):
    # base message viewer

    if request.user.is_superuser:
        return redirect('/dashboard')

    received = Message.objects.filter(receiver=request.user).order_by('-created')
    sent = Message.objects.filter(sender=request.user).order_by('-created')
    return render_to_response('messenger.html',{'received': received, 'sent': sent}, context_instance=RequestContext(request))

    #form = MessagerForm(request.POST or None, instance=Message.objects.get(reciever = request.user))
    #return render(request, 'messenger.html', {'form': form})

@login_required
def deleteMessage(request, id):
    #simply deletes the message object selected

    if request.user.is_superuser:
        return redirect('/dashboard')

    Message.objects.filter(id=id).delete()
    return render(request, 'deleteMessage.html')

@login_required
def Compose(request, username=''):
    #creates the message using the compose form

    if request.user.is_superuser:
        return redirect('/dashboard')

    if request.method == 'POST':
        form = ComposeForm(data=request.POST, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('/messenger')
    else:
        form = ComposeForm(user=request.user, username=username)
        #form = ComposeForm(username=username)
    return render(request, 'compose.html',{'form': form},)

@login_required
def profileView(request, username):

    if request.user.is_superuser:
        return redirect('/dashboard')

    try:
        profileUser = User.objects.get(username=username)
    except User.DoesNotExist:
        return HttpResponse('<h1>User not found</h1>')

    try:
        profilePatient = Patient.objects.get(user=profileUser)
    except Patient.DoesNotExist:
        profilePatient = None

    try:
        profileDoctor = Doctor.objects.get(user=profileUser)
    except Doctor.DoesNotExist:
        profileDoctor = None

    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        patient = None

    try:
        doctor = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        doctor = request.user

    if patient != None:
        #user logged in is a patient
        if profilePatient != None:
            #it's a patient viewing a patient's profile
            return render(request, 'profile.html', {'profileUser': profileUser, 'profile': profilePatient, 'type': 'patient', 'profiletype': 'patient'})
        elif profileDoctor != None:
            #it's a patient viewing a doctor's profile
            return render(request, 'profile.html', {'profileUser': profileUser, 'profile': profileDoctor, 'type': 'patient', 'profiletype': 'doctor'})
    elif doctor != None:
        #user logged in is a doctor
        if profilePatient != None:
            #it's a doctor viewing a patient's profile
            return render(request, 'profile.html', {'profileUser': profileUser, 'profile': profilePatient, 'type': 'doctor', 'profiletype': 'patient'})
        elif profileDoctor != None:
            #it's a doctor viewing a doctor's profile
            return render(request, 'profile.html', {'profileUser': profileUser, 'profile': profileDoctor, 'type': 'doctor', 'profiletype': 'doctor'})

    return render(request, 'profile.html', {'profileUser': profileUser})

@login_required
def fileView(request, filename):

    if request.user.is_superuser:
        return redirect('/dashboard')

    path_to_file = 'media/healthnetfiles/' + filename
    name, extension = filename.split('.')
    if extension == 'txt':
        test_file = open(path_to_file, 'rb')
        response = HttpResponse(content=test_file)
        response['Content-Type'] = 'text/plain; charset=utf-8'
        return response
    if extension == 'pdf':
        test_file = open(path_to_file, 'rb')
        response = HttpResponse(content=test_file)
        response['Content-Type'] = 'application/pdf; charset=utf-8'
        return response
    if extension == 'docx' or extension == 'doc':
        test_file = open(path_to_file, 'rb')
        response = HttpResponse(content=test_file)
        response['Content-Type'] = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document; charset=utf-8'
        return response
    if extension == 'png':
        test_file = open(path_to_file, 'rb')
        response = HttpResponse(content=test_file)
        response['Content-Type'] = 'image/png; charset=utf-8'
        return response
    if extension == 'gif':
        test_file = open(path_to_file, 'rb')
        response = HttpResponse(content=test_file)
        response['Content-Type'] = 'image/gif; charset=utf-8'
        return response
    if extension == 'jpg' or extension=='jpeg':
        test_file = open(path_to_file, 'rb')
        response = HttpResponse(content=test_file)
        response['Content-Type'] = 'image/jpeg; charset=utf-8'
        return response
    test_file = open(path_to_file, 'rb')
    response = HttpResponse(content=test_file)
    return response
    #files = HealthFiles.objects.filter(ptient=Patient.objects.filter(user = request.user))
    #return render_to_response('fileView.html', {'files': files},context_instance=RequestContext(request))

@login_required
def UploadFile(request):

    if request.user.is_superuser:
        return redirect('/dashboard')

    try:
        doctor = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        doctor = None

    if doctor == None:
        return redirect('/dashboard')

    if request.method == 'POST':
        form = HealthFileForm(request.POST,request.FILES)
        if form.is_valid():
            healthfile = HealthFiles.create(doctor, form.cleaned_data['patient'], request.FILES['docfile'], form.cleaned_data['comment'], form.cleaned_data['canview'])
            healthfile.save()
            Entry.objects.createEntry(request.user, 'file upload', datetime.datetime.now())
            #instance = HealthFiles.objects.filter(doctor=Doctor.objects.filter(user=request.user)).docfile=request.FILES['file']
            #instance.save()
            return redirect('/dashboard')
    else:
        print("fail")
        form = HealthFileForm()
    return render(request, 'UploadFile.html',{'form': form},)

@login_required
def dashboard(request):
    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        patient = None

    try:
        doctor = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        doctor = None

    if request.user.is_superuser:
        type = 'admin'

        num_of_logins = Entry.objects.filter(message='user login').count()
        query_result = Entry.objects.filter(message='user login').values('user').annotate(num_logins=Count('id'))
        for result in query_result:
            result['avg_logins'] = (result['num_logins']/num_of_logins) * 100

        query_result2 = None
    elif patient != None:
        #They're a patient
        type = 'patient'
        query_result = Appointment.objects.filter(ptient = patient).values().order_by('-when')
        if query_result:
            for item in query_result:
        #    item['name']='Bob'
                item['name'] = Doctor.objects.get(id = item['dr_id'])
        else:
            #no query_results
            query_result = None

        query_result2 = HealthFiles.objects.filter(patient = patient, canview = True).values()
        if query_result2:
            #they have viles
            pass
        else:
            query_result2 = None
    elif doctor != None:
        #They're a doctor
        type='doctor'
        query_result = Appointment.objects.filter(dr = doctor).values()
        if query_result:
            for item in query_result:
                #add patient name
                item['name'] = Patient.objects.get(id = item['ptient_id'])
        else:
            #no query_results
            query_result = None

        query_result2 = None
    else:
        query_result = None

    return render(request, 'dashboard.html', {'query_result': query_result, 'type':type, 'query_result2': query_result2})

def index(request):
    #redirect if user is authenticated
    if request.user.is_authenticated():
        return redirect('dashboard')

    return render(request, 'index.html')

@login_required
def createAppointment(request):

    if request.user.is_superuser:
        return redirect('/dashboard')

    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        return redirect('calendar')

    if request.method == 'POST':
        form = CreateAppointmentForm(data=request.POST, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('/calendar')
    else:
        form = CreateAppointmentForm(user=request.user)
    return render(request, 'createAppointment.html',{'form': form})

@login_required
def calendar(request):

    if request.user.is_superuser:
        return redirect('/dashboard')

    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        patient = None

    try:
        doctor = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        doctor = None

    if patient != None:
        #They're a patient.
        type = 'patient'
        appointments = Appointment.objects.filter(dr = patient.doctor)
    elif doctor != None:
        type = 'doctor'
        appointments = Appointment.objects.filter(dr = doctor)
    else:
        appointments = None

    appointmentlist = []
    for appointment in appointments:
        # start = appointment.when - datetime.timedelta(hours=4)
        start = localtime(appointment.when)
        # end = appointment.endtime - datetime.timedelta(hours=4)
        end = localtime(appointment.endtime)
        #newstart = appointment.when - datetime.timedelta(hours=4)
        #newend = appointment.endtime - datetime.timedelta(hours=4)
        title = str(start.strftime('%H:%M')) + " - " + str(end.strftime('%H:%M')) + " " + appointment.ptient.first_name + " " + appointment.ptient.last_name

        appointmentlist.append({'title': title, 'start': start, 'end': end})

    '''
    calendar_config_options = {'header': {
        'left': 'prev,next today',
        'center': 'title',
        'right': 'month,agendaWeek,agendaDay'
    },
        'defaultView': 'agendaWeek',
        'editable': 'True',  # View only.
        'events': json.dumps(appointmentlist),
        'firstDay': 1  # Week starts on Monday.
    }'''

    event_url = 'calendarEvents/'

    #return HttpResponse(events_to_json(appointments), content_type='application/json')
    return render(request, 'calendar.html', {'appointmentlist': json.dumps(appointmentlist, default=date_handler), 'type': type, 'patient': patient})

@login_required
def deleteAppointment(request):
    if request.user.is_superuser:
        return redirect('/dashboard')

    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        patient = None

    try:
        doctor = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        doctor = None

    if request.method == 'POST':
        if patient != None:
            # They're a patient
            form = DeleteAppointmentForm(data=request.POST, type='patient', user=patient)

            if request.POST['when'] != "":
                apptToDelete = Appointment.objects.filter(id = request.POST['when'])
                apptToDelete.delete()

            return redirect('/calendar')

        elif doctor != None:
            # They're a doctor.
            form = DeleteAppointmentForm(data=request.POST, type='doctor', user=doctor)

            if request.POST['when'] != "":
                apptToDelete = Appointment.objects.filter(id=request.POST['when'])
                apptToDelete.delete()

            return redirect('/calendar')
    else:
        if patient != None:
            # They're a patient
            form = DeleteAppointmentForm(type='patient', user=patient)

        elif doctor != None:
            # They're a doctor.
            form = DeleteAppointmentForm(type='doctor', user=doctor)




    return render(request, 'deleteAppointment.html', {'form': form})

