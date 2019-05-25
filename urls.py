from django.conf.urls import url
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
               url(r'^$', views.index, name='index'),
               # ex: /FlightLog/
               url(r'add_sorties', views.add_sorties, name='add_sorties'),
               # ex: /FlightLog/add_sorties
               url(r'calendar\.', views.view_calendar, name='calendar'),
               # ex: /FlightLog/calendar.
               url(r'calendar_add', views.calendar_add, name='calendar_add'),
               # ex: /FlightLog/calendar_add
               url(r'delete_from_db', views.delete_from_db, name='delete_from_db'),
               # ex: /FlightLog/delete_from_db
               url(r'settings', views.settings, name='settings'),
               # ex: /FlightLog/settings
               url(r'history', views.history, name='history'),
               # ex: /FlightLog/settings
               url(r'^login/$', auth_views.login,{'template_name': 'FlightLog/login.html'},),
               # ex: /FlightLog/login
               url(r'^flight_log/(?P<pk>[0-9]+)/delete/$',views.delete_flight, name='flight_log_delete'),
               # ex: /FlightLog/flight_log/1024/delete
               ]