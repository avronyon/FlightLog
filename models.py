from __future__ import unicode_literals

from django.db import models

from django.utils import timezone

# Create your models here.

class goals(models.Model):
    pilot = models.CharField(max_length=200)
    mission = models.CharField(max_length=200)
    value = models.IntegerField(default=0)
    
class flightLog(models.Model):
    pilot = models.CharField(max_length=200)
    mission = models.CharField(max_length=200,blank=True,null=True)
    dt =  models.DateField('date of occurence')
    
class plannedFlight(models.Model):
    pilot = models.CharField(max_length=200)
    day_value = models.IntegerField(default=2)
    night_value = models.IntegerField(default=0)
    gnd_activity = models.CharField(max_length=200,blank=True,null=True)
    iCalUID = models.CharField(max_length=200,blank=True,null=True)
    dt =  models.DateField('date of occurence')