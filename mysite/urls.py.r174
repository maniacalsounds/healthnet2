"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from HealthNet.views import index, fileView, E_contact_view , E_contact_create_View, prescriptionView, createPrescription, deletePrescription, admission, transfer, UploadFile, register, deleteMessage, login, logout, update, dashboard, calendar, createAppointment, deleteAppointment, Messenger, Compose

urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'^admin/', admin.site.urls),
    #url(r'^calendar/', calendar, name='calendar'),
    url(r'^register/', register, name='register'),
    url(r'^login/', login, name='login'),
    url(r'^messenger/', Messenger, name='messenger'),
    url(r'^fileView/', fileView, name='fileView'),
    url(r'^transfer/', transfer, name='transfer'),
    url(r'^E_contact_view/', E_contact_view, name='E_contact_view'),
    url(r'^E_contact_create/', E_contact_create_View, name='E_contact_create'),
    url(r'^createPrescription/', createPrescription, name='createPrescription'),
    url(r'^admission/', admission, name='admission'),
    url(r'^prescriptionView/', prescriptionView, name='prescriptionView'),
    url(r'^deletePrescription/(?P<id>[0-9]+)/', deletePrescription, name='delete Prescription'),
    url(r'^deleteMessage/(?P<id>[0-9]+)/', deleteMessage, name='delete Message'),
    url(r'^compose/', Compose, name='compose'),
    url(r'^UploadFile/', UploadFile, name='UploadFile'),
    url(r'^update/', update, name='update'),
    url(r'^dashboard/', dashboard, name='dashboard'),
    url(r'calendar/', calendar, name='calendar'),
    #url(r'^login/', django.contrib.auth.views.login, name='login'),
    url(r'^logout/', logout, name='logout'),
    url(r'^createAppointment/', createAppointment, name='create appointment'),
    url(r'^deleteAppointment/', deleteAppointment, name='delete appointment'),
    url(r'^viewfile/(?P<filename>[A-Za-z0-9.]+)/', fileView, name='view file'),
    url(r'^media/healthnetfiles/(?P<filename>[A-Za-z0-9._\-]+)/', fileView, name='view file'),
    #url(r'profile/(?P<username>[0-9]+)/'),
    #url(r'^accounts/', include('accounts.urls', namespace='accounts')),
]
