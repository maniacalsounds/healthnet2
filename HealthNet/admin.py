from django.contrib import admin
from .models import Doctor, Hospital, Patient, Appointment, Nurse, HealthFiles

# Register your models here.

class patientAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Username', {'fields': ['user']}),
        ('First name', {'fields': ['first_name']}),
        ('Last name', {'fields': ['last_name']}),
        ('Sex', {'fields': ['sex']}),
        ('Assigned doctor', {'fields': ['doctor']}),
        ('Insurance policy number', {'fields': ['insurance_num']}),
        ('Weight', {'fields': ['weight']}),
        ('Height (ft)', {'fields': ['height_ft']}),
        ('Height (in)', {'fields': ['height_in']}),
        ('Home address', {'fields': ['address']}),
        ('Phone number', {'fields': ['phone_number']}),
        ('Contact e-mail', {'fields': ['email']}),
        ('Emergency Contact Username', {'fields': ['E_contact']}),
        ('Emergency Contact Name', {'fields':['E_contact_name']}),
        ('Emergency Contact Address', {'fields': ['E_contact_address']}),
        ('Preferred hospital', {'fields': ['preferred_hospital']}),
        ('Admitted to', {'fields': ['cur_hospital']}),
    ]
    list_display = ('user', 'first_name', 'last_name', 'sex', 'doctor')
    search_fields = ['user__username', 'first_name', 'last_name', 'sex', 'doctor__user__username']

admin.site.register(Patient, patientAdmin)

class hospitalAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Hospital name', {'fields': ['name']}),
        ('Hospital address', {'fields': ['location']}),
    ]
    list_display = ('name', 'location')
    search_fields = ['name', 'location']

admin.site.register(Hospital, hospitalAdmin)

class appointmentAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Time', {'fields': ['when', 'endtime']}),
        #('End Time', {'fields': ['endtime']}),
        ('Doctor', {'fields': ['dr']}),
        ('Patient', {'fields': ['ptient']}),
    ]
    list_display = ('when', 'dr', 'ptient', 'endtime')
    search_fields = ['when', 'dr__user', 'ptient__user', 'endtime']

admin.site.register(Appointment, appointmentAdmin)

class doctorAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Username', {'fields': ['user']}),
        ('First name', {'fields': ['first_name']}),
        ('Last name', {'fields': ['last_name']}),
        ('Home address', {'fields': ['address']}),
        ('Phone number', {'fields': ['phone_number']}),
        ('Contact e-mail', {'fields': ['email']}),
        ('Hospital', {'fields': ['hospital']}),
    ]
    list_display = ('user', 'first_name', 'last_name', 'address', 'phone_number', 'email', 'hospital')
    search_fields = ['user__username', 'first_name', 'last_name', 'email', 'hospital__name']
    def queryset(self, request):
        qs = super(doctorAdmin, self).queryset(request)
        if request.user.is_superuser:
            return qs
        if isDoctor(request.user):
            return qs.filter(user=request.user)

admin.site.register(Doctor, doctorAdmin)

class nurseAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Username', {'fields': ['user']}),
        ('First name', {'fields': ['first_name']}),
        ('Last name', {'fields': ['last_name']}),
        ('Home address', {'fields': ['address']}),
        ('Phone number', {'fields': ['phone_number']}),
        ('Contact e-mail', {'fields': ['email']}),
        ('Hospital', {'fields': ['hospital']}),
    ]
    list_display = ('user', 'first_name', 'last_name', 'address', 'phone_number', 'email', 'hospital')
    search_fields = ['user__username', 'first_name', 'last_name', 'email', 'hospital__name']

admin.site.register(Nurse, nurseAdmin)

class healthFilesAdmin(admin.ModelAdmin):
    fieldsets = [
        ('docfile', {'fields': ['docfile']}),
        ('patient', {'fields': ['patient']}),
        ('doctor', {'fields': ['doctor']}),
        ('comment', {'fields': ['comment']}),
    ]
    list_display = ('docfile', 'patient', 'doctor', 'comment')

admin.site.register(HealthFiles, healthFilesAdmin)

def isDoctor(user):
    return user.groups.filter(name__in=['Doctors']).exists()

def isPatient(user):
    return user.groups.filter(name__in=['Patients']).exists()

def isNurse(user):
    return user.groups.filter(name__in=['Nurses']).exists()