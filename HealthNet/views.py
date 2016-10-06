
# Create your views here.
from collections import OrderedDict

from django.contrib.auth.decorators import login_required
#from django.core.serializers import json
import simplejson as json
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import render_to_response, redirect, render
from django.template import RequestContext, context
from django.contrib.auth import login as django_login, authenticate, logout as django_logout
from django.http import HttpResponse
from django.templatetags.tz import localtime

from log.models import Entry
from simplejson.encoder import i

from .forms import PatientRegisterForm, AuthenticationForm, UpdatePatientForm, UpdateDoctorForm, CreateAppointmentForm, \
    DeleteAppointmentForm
from datetime import date
from .models import Appointment, Patient, Doctor
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
def update(request):
    """
    User registration view.
    """
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
def dashboard(request):
    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        patient = None

    try:
        doctor = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        doctor = None

    if patient != None:
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
    else:
        query_result = None

    return render(request, 'dashboard.html', {'query_result': query_result, 'type':type})

def index(request):
    #redirect if user is authenticated
    if request.user.is_authenticated():
        return redirect('dashboard')

    return render(request, 'index.html')

@login_required
def createAppointment(request):
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

        elif doctor != None:
            # They're a doctor.
            form = DeleteAppointmentForm(data=request.POST, type='doctor', user=doctor)

        if form.is_valid():
            #form.save()
            return redirect('/calendar')
    else:
        if patient != None:
            # They're a patient
            form = DeleteAppointmentForm(type='patient', user=patient)

        elif doctor != None:
            # They're a doctor.
            form = DeleteAppointmentForm(type='doctor', user=doctor)




    return render(request, 'deleteappointment.html', {'form': form})

'''
def calendar(request, year, month, series_id=None):
    """
    Show calendar of events for a given month of a given year.
    ``series_id``
    The event series to show. None shows all event series.

    """

    my_year = int(year)
    my_month = int(month)
    my_calendar_from_month = datetime.datetime(my_year, my_month, 1)
    my_calendar_to_month = datetime.datetime(my_year, my_month, monthrange(my_year, my_month)[1])

    my_events = Appointment.objects.all().filter(when=my_calendar_from_month).filter(when=my_calendar_to_month)
    #if series_id:
     #   my_events = my_events.filter(series=series_id)

    # Calculate values for the calendar controls. 1-indexed (Jan = 1)
    my_previous_year = my_year
    my_previous_month = my_month - 1
    if my_previous_month == 0:
        my_previous_year = my_year - 1
        my_previous_month = 12
    my_next_year = my_year
    my_next_month = my_month + 1
    if my_next_month == 13:
        my_next_year = my_year + 1
        my_next_month = 1
    my_year_after_this = my_year + 1
    my_year_before_this = my_year - 1 #This template name needs to change
    return render_to_response("cal_template.html", { 'events_list': my_events,
                                                        'month': my_month,
                                                        'month_name': named_month(my_month),
                                                        'year': my_year,
                                                        'previous_month': my_previous_month,
                                                        'previous_month_name': named_month(my_previous_month),
                                                        'previous_year': my_previous_year,
                                                        'next_month': my_next_month,
                                                        'next_month_name': named_month(my_next_month),
                                                        'next_year': my_next_year,
                                                        'year_before_this': my_year_before_this,
                                                        'year_after_this': my_year_after_this,
    }, context_instance=RequestContext(request))
'''
