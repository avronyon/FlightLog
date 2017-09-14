# coding=UTF-8

from django.shortcuts import render
from django.http import HttpResponse , HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils.safestring import mark_safe
import datetime
import re
import myHTMLCalendar
from .models import goals , flightLog , plannedFlight

# Create your views here.

PIRIOD_S = datetime.datetime(2017,7,1,0,0,0)
PIRIOD_E = datetime.datetime(2017,12,31,0,0,0)
GND_ACTIONS = ('sim','sim_winter','malam','yarpa')

	
def get_flights(pilot_name,mission='total'):
	if mission == 'total':
		mission = ''
	try:
		# notice we do not count ground activities
		return len(flightLog.objects.filter(pilot=pilot_name).filter(dt__gte = PIRIOD_S).filter(mission__contains=mission).exclude(mission__contains='gnd'))
	except:
		return 0
		
def get_goal(pilot_name,mission='total'):
	try:
		return goals.objects.filter(pilot=pilot_name).filter(mission=mission)[0].value
	except:
		return 'undefined'

def get_potential(pilot_name):
	total_p = get_flights(pilot_name,'total')
	night_p = get_flights(pilot_name,'night')
	for flight in plannedFlight.objects.filter(pilot=pilot_name).filter(dt__gt = datetime.datetime.today()):
		total_p += (flight.day_value + flight.night_value)
		night_p += flight.night_value
	return total_p , night_p

def get_gnd_activity(pilot_id):
	done = flightLog.objects.filter(pilot=pilot_id).filter(dt__gte = PIRIOD_S).filter(mission__contains='gnd')
	planned = plannedFlight.objects.filter(pilot=pilot_id).filter(dt__gt = datetime.datetime.today()).filter(gnd_activity__isnull=False)
	out = ''
	for f in done:
		out += '<td bgcolor="#ffb23f">'+f.mission.strip(';')+'</td>'
	for f in planned:
		out += '<td>'+f.gnd_activity.strip(';')+'</td>'
	out = out.replace('gnd_sim_winter', u'🌧️').replace('gnd_sim', u'🔥').replace('gnd_malam', u'🕹️').replace('gnd_yarpa', u'💉')
	return out
	
@login_required
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

@login_required
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
			print mission_dict[int(sortie_num)]
		for sortie in mission_dict:
			sortie_entry = flightLog(pilot=pilot_id, mission=mission_dict[sortie],dt=request.POST['date'])
			sortie_entry.save()
		return HttpResponseRedirect("/FlightLog/")
	else:
		return render(request, 'FlightLog/add_sorties.html', {'pilot_name': pilot_id,})

@login_required	
def view_calendar(request):
	pilot_id = request.user.id
	date = datetime.datetime.strptime(request.GET['date'],'%Y-%m-%d')
	year = int(date.year)
	month = int(date.month)
	#year = int(request.GET['date'].year)
	#month = int(request.GET['date'].month)
	next_cal = datetime.date(year,month,1) + datetime.timedelta(31,0,0)
	prev_cal = datetime.date(year,month,1) - datetime.timedelta(3,0,0)
	done_sorties = flightLog.objects.filter(pilot=pilot_id).filter(dt__gte = prev_cal).values_list('dt', flat=True)
	planned_sorties = plannedFlight.objects.filter(pilot=pilot_id).filter(dt__gte = datetime.datetime.today()).filter(dt__lte = next_cal).values_list('dt', flat=True)
	c = myHTMLCalendar.MyHTMLCalendar(done_sorties,planned_sorties)
	c.setfirstweekday(6)
	return render(request, 'FlightLog/calendar.html', {'Calendar': mark_safe(c.formatmonth(year,month)),'next_year':next_cal.year,'next_month':next_cal.month,'prev_year':prev_cal.year,'prev_month':prev_cal.month})

@login_required
def calendar_add(request):
	pilot_id = request.user.id
	if request.method == 'POST':
		sortie_entry = plannedFlight(pilot=pilot_id, day_value=request.POST['day'],night_value=request.POST['night'],dt=request.POST['date'])
		sortie_entry.save()
		return HttpResponseRedirect("/FlightLog/calendar.html?date="+request.POST['date'])
	else:
		return render(request, 'FlightLog/calendar_add.html', {'pilot_name': pilot_id,})
	
@login_required	
def delete_from_db(request):
	pilot_id = request.user.id
	if request.method == 'POST':
		plannedFlight.objects.filter(pilot=pilot_id).filter(dt = request.POST['date']).delete()
		flightLog.objects.filter(pilot=pilot_id).filter(dt = request.POST['date']).delete()
		return HttpResponseRedirect("/FlightLog/calendar.html?date="+request.POST['date'])
	else:
		return render(request, 'FlightLog/calendar_delete.html')

@login_required			
def settings(request):
	pilot_id = request.user.id
	if request.method == 'POST':
		for new_goal in request.POST:
			try:
				goal = goals.objects.get(pilot=pilot_id,mission=new_goal)
				goal.value = request.POST[new_goal]
				print new_goal
				goal.save()
			except:
				pass
		return HttpResponseRedirect("/FlightLog/")
	else:
		return render(request, 'FlightLog/settings.html')
		
@login_required
def history(request):
	pilot_id = request.user.id
	flight_list = flightLog.objects.filter(pilot=pilot_id).order_by('-dt')
	for flight in flight_list:
		flight.mission = flight.mission.replace(';',' ').strip()
		if flight.mission == '':
			flight.mission = 'day'
	return render(request, 'FlightLog/history.html', {'flight_list':flight_list,})