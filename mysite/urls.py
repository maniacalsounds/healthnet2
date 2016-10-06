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
from HealthNet.views import index, register, login, logout, update, dashboard, calendar, createAppointment, deleteAppointment

urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'^admin/', admin.site.urls),
    url(r'^register/', register, name='register'),
    url(r'^login/', login, name='login'),
    url(r'^update/', update, name='update'),
    url(r'^dashboard/', dashboard, name='dashboard'),
    url(r'calendar/', calendar, name='calendar'),
    #url(r'^login/', django.contrib.auth.views.login, name='login'),
    url(r'^logout/', logout, name='logout'),
    url(r'^createAppointment/', createAppointment, name='create appointment'),
    url(r'^deleteAppointment/', deleteAppointment, name='delete appointment'),
    #url(r'^accounts/', include('accounts.urls', namespace='accounts')),
]
