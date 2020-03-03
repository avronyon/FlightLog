from __future__ import absolute_import
from django.contrib import admin

# Register your models here.

from .models import goals,flightLog, plannedFlight

admin.site.register(flightLog)
admin.site.register(goals)
admin.site.register(plannedFlight)