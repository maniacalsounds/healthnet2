from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models

# Create your models here.
class EntryManager(models.Manager):
    def createEntry(self, user, message, date):
        entry = self.create(user=user, message=message, date=date)
        return entry

class Entry(models.Model):
    user = models.ForeignKey(User)
    message = models.CharField(max_length=100,blank=True)
    date = models.DateTimeField()
    objects = EntryManager()