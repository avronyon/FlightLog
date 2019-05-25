# -*- coding: utf-8 -*-

from django import template
from django.template.defaulttags import register

@register.filter
def mission_hebrew(value):
	s = {'gnd_malam':'מלאמ',
		'gnd_sim_winter':'מבחן חורף',
		'gnd_sim':'סימולטור',
		'gnd_konan':'כוננות',
		'gnd_yarpa':'ירפא',
		'night':'לילה',
		'shoham':'שוהם',
		'recon':'צילום',
		'day':'יום',
		}
	try:
		out = ''
		for a in value.split():
			out += s[a]+' '
		return out
	except:
		return value