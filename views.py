# coding=UTF-8

from __future__ import absolute_import
from django.shortcuts import render
from django.http import HttpResponse , HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils.safestring import mark_safe
from django.db import connections
from django.contrib.auth.decorators import user_passes_test
from django.views.generic.edit import DeleteView
from django.urls import reverse
import datetime
import uuid , os
import subprocess
import re
from . import myHTMLCalendar
from .models import goals , flightLog , plannedFlight

# Create your views here.

PIRIOD_S = datetime.datetime(2020,1,2,0,0,0)
PIRIOD_E = datetime.datetime(2020,6,27,0,0,0)
GND_ACTIONS = ('sim','sim_winter','malam','yarpa','konan')
STATIC_SIM_GOAL = 2
STATIC_MALAM_GOAL = 2
CALENDAR_SCRIPT_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__),os.path.pardir,('calendar_manager')))

def is_pilot(user):
	return user.groups.filter(name='pilots').exists()

def emoji_replace(s):
	return s.replace('gnd_sim_winter', u'🌧️').replace('gnd_sim', u'🔥').replace('gnd_malam', u'🕹️').replace('gnd_yarpa', u'💉').replace('fullmoon',u'🌔').replace('gnd_konan', u'🏖')


def get_flights(pilot_name,mission='total'):
	n = 0
	if mission == 'total':
		mission = ''
		## add gnd_malam missions as they are counted for total air missions
		n = len(flightLog.objects.filter(pilot=pilot_name).filter(dt__gte = PIRIOD_S).filter(mission__contains='gnd_malam'))
	try:
		# notice we do not count ground activities
		return n + len(flightLog.objects.filter(pilot=pilot_name).filter(dt__gte = PIRIOD_S).filter(mission__contains=mission).exclude(mission__contains='gnd'))
	except:
		return 0
		
def get_goal(pilot_name,mission='total'):
	try:
		return goals.objects.filter(pilot=pilot_name).filter(mission=mission)[0].value
	except:
		if mission == 'gnd_sim':
			return STATIC_SIM_GOAL
		if mission == 'gnd_malam':
			return STATIC_MALAM_GOAL
		return 'undefined'

def get_potential(pilot_name):
	# currently potential doesn't include malaam
	total_p = get_flights(pilot_name,'total')
	night_p = get_flights(pilot_name,'night')
	for flight in plannedFlight.objects.filter(pilot=pilot_name).filter(dt__gt = datetime.datetime.today()):
		total_p += (flight.day_value + flight.night_value)
		night_p += flight.night_value
	return total_p , night_p

def get_gnd_activity(pilot_id):
	done = flightLog.objects.filter(pilot=pilot_id).filter(dt__gte = PIRIOD_S).filter(mission__contains='gnd').order_by('dt')
	planned = plannedFlight.objects.filter(pilot=pilot_id).filter(dt__gt = datetime.datetime.today()).filter(gnd_activity__isnull=False).order_by('dt')
	out = ''
	## clean excess ';'
	for f in done:
		f.mission = f.mission.strip(';')
		f.save()
	###
	done = done.values('mission','dt').distinct()
	for f in done:
		out += '<td bgcolor="#ffb23f">'+f['mission'].strip(';')+'</td>'
	for f in planned:
		out += '<td style="filter:grayscale(30%)">'+f.gnd_activity.strip(';')+'</td>'
	# padding with goals
	while(out.count('sim')< get_goal(pilot_id,mission='gnd_sim')):
		out += '<td style="filter:grayscale(100%)">gnd_sim</td>'
	while(out.count('malam')< get_goal(pilot_id,mission='gnd_malam')):
		out += '<td style="filter:grayscale(100%)">gnd_malam</td>'
	if len(flightLog.objects.filter(pilot=pilot_id).filter(dt__gte = datetime.datetime(PIRIOD_E.year - 1,PIRIOD_E.month,PIRIOD_E.day)).filter(mission__contains = 'gnd_yarpa')) == 0 and not 'yarpa' in out:
		 out += '<td style="filter:grayscale(100%)">gnd_yarpa</td>'
	return emoji_replace(out)
	
#@login_required(login_url='/FlightLog/login/')
@user_passes_test(is_pilot,login_url='/FlightLog/login/')
def index(request):
	pilot_id = request.user.id
	return render(request, 'FlightLog/front_page.html', {
		'total_done': get_flights(pilot_id),
		'total_goal':get_goal(pilot_id) ,
		'total_potential':get_potential(pilot_id)[0],
		'night_done': get_flights(pilot_id,'night'),
		'night_goal':get_goal(pilot_id,'night'),
		'night_potential':get_potential(pilot_id)[1],
		'gnd_plan':len(plannedFlight.objects.filter(pilot=pilot_id).filter(dt__gt = datetime.datetime.today()).filter(gnd_activity__isnull=False)),
		'gnd_done' : len(flightLog.objects.filter(pilot=pilot_id).filter(dt__gte = PIRIOD_S).filter(mission__contains='gnd')),
		'gnd_activity_table': get_gnd_activity(pilot_id),
		'piriod_l':(PIRIOD_E-PIRIOD_S).days ,
		'piriod_elapsed':(datetime.datetime.now()-PIRIOD_S).days
		})

@user_passes_test(is_pilot,login_url='/FlightLog/login/')
def add_sorties(request):
	pilot_id = request.user.id
	if request.method == 'POST':
		mission_dict = {}
		for mission in request.POST:
			try:
				sortie_num = re.findall(r'\d+',mission)[0]
			except:
				continue
			mission_value = mission[len('mission')+len(sortie_num):]
			if mission_value in GND_ACTIONS:
				mission_value = 'gnd_'+mission_value
			try:
				mission_dict[int(sortie_num)] += mission_value + ';'
			except:
				mission_dict[int(sortie_num)] = mission_value + ';'
		for sortie in mission_dict:
			sortie_entry = flightLog(pilot=pilot_id, mission=mission_dict[sortie],dt=request.POST['date'])
			sortie_entry.save()
		return HttpResponseRedirect("/FlightLog/")
	else:
		return render(request, 'FlightLog/add_sorties.html', {'pilot_name': pilot_id,})

@user_passes_test(is_pilot,login_url='/FlightLog/login/')
def view_calendar(request):
	pilot_id = request.user.id
	date = datetime.datetime.strptime(request.GET['date'],'%Y-%m-%d')
	year = int(date.year)
	month = int(date.month)
	next_cal = datetime.date(year,month,1) + datetime.timedelta(31,0,0)
	prev_cal = datetime.date(year,month,1) - datetime.timedelta(3,0,0)
	done_sorties = flightLog.objects.filter(pilot=pilot_id).filter(dt__gte = prev_cal).values_list('dt', flat=True)
	planned_sorties = plannedFlight.objects.filter(pilot=pilot_id).filter(dt__gte = datetime.datetime.today()).filter(dt__lte = next_cal).values_list('dt', flat=True)
	c = myHTMLCalendar.MyHTMLCalendar(pilot_id,done_sorties,planned_sorties)
	c.setfirstweekday(6)
	return render(request, 'FlightLog/calendar.html', {'Calendar': mark_safe(emoji_replace(c.formatmonth(year,month))),'next_year':next_cal.year,'next_month':next_cal.month,'prev_year':prev_cal.year,'prev_month':prev_cal.month})

@user_passes_test(is_pilot,login_url='/FlightLog/login/')
def calendar_add(request):
	pilot_id = request.user.id
	iCalUID = 'UNSYNCED_'+uuid.uuid4().hex
	if request.method == 'POST':
		sortie_entry = plannedFlight(pilot=pilot_id,iCalUID = iCalUID, day_value=request.POST['day'],night_value=request.POST['night'],dt=request.POST['date'])
		if not request.POST['gnd_activity'] == 'none':
			sortie_entry.gnd_activity = request.POST['gnd_activity']
		sortie_entry.save()
		sqliteDB = '"'+os.path.abspath(connections.databases['default']['NAME'])+'"'
		cmd = 'python calendar-manager.py --sqliteDB %s --add %s' %(sqliteDB,iCalUID)
		p = subprocess.Popen([cmd],cwd=CALENDAR_SCRIPT_DIR,shell=True)
		return HttpResponseRedirect("/FlightLog/calendar.html?date="+request.POST['date'])
	else:
		return render(request, 'FlightLog/calendar_add.html', {'pilot_name': pilot_id,})
	
@user_passes_test(is_pilot,login_url='/FlightLog/login/')
def delete_from_db(request):
	pilot_id = request.user.id
	if request.method == 'POST':
		try:
			for flight in plannedFlight.objects.filter(pilot=pilot_id).filter(dt = request.POST['date']):
				iCalUID = flight.iCalUID
			sqliteDB = '"'+os.path.abspath(connections.databases['default']['NAME'])+'"'
			cmd = 'python calendar-manager.py --sqliteDB %s --delete %s' %(sqliteDB,iCalUID)
			p = subprocess.Popen([cmd],cwd=CALENDAR_SCRIPT_DIR,shell=True)
		except:
			pass
		plannedFlight.objects.filter(pilot=pilot_id).filter(dt = request.POST['date']).delete()
		flightLog.objects.filter(pilot=pilot_id).filter(dt = request.POST['date']).delete()
		return HttpResponseRedirect("/FlightLog/calendar.html?date="+request.POST['date'])
	else:
		return render(request, 'FlightLog/calendar_delete.html')

@user_passes_test(is_pilot,login_url='/FlightLog/login/')
def settings(request):
	pilot_id = request.user.id
	if request.method == 'POST':
		for new_goal in request.POST:
			if new_goal in ('total','night','gnd_malam','gnd_sim'):
				try:
					goal = goals.objects.get(pilot=pilot_id,mission=new_goal)
					goal.value = request.POST[new_goal]
					goal.save()
				except:
					try:
						goal = goals(pilot=pilot_id,mission=new_goal,value=request.POST[new_goal])
						goal.save()
					except:
						pass
		return HttpResponseRedirect("/FlightLog/")
	else:
		return render(request, 'FlightLog/settings.html')
		
@user_passes_test(is_pilot,login_url='/FlightLog/login/')
def history(request):
	pilot_id = request.user.id
	flight_list = flightLog.objects.filter(pilot=pilot_id).order_by('-dt')
	for flight in flight_list:
		flight.mission = flight.mission.replace(';',' ').strip()
		if flight.mission == '':
			flight.mission = 'day'
	return render(request, 'FlightLog/history.html', {
		'flight_list':flight_list,
		'last_night': flightLog.objects.filter(pilot=pilot_id).filter(mission__contains='night').order_by('-dt'),
		'last_shoham':flightLog.objects.filter(pilot=pilot_id).filter(mission__contains='shoham').order_by('-dt'),})

@user_passes_test(is_pilot,login_url='/FlightLog/login/')
def delete_flight(request,pk):
	pilot_id = request.user.id
	if request.method == 'POST':
		flightLog.objects.filter(pilot=pilot_id,id=pk).delete()
		return HttpResponseRedirect(reverse('history'))
	else:
		return render(request, 'FlightLog/flight_delete.html')