from calendar import HTMLCalendar
from datetime import date


class MyHTMLCalendar(HTMLCalendar):
	def __init__(self,done_sorties,planned_sorties):
		super(MyHTMLCalendar, self).__init__()
		self.done_sorties = done_sorties
		self.planned_sorties = planned_sorties
	
	def formatday(self, day, weekday):
		"""
		Return a day as a table cell.
		"""
		if day == 0:
			return self.day_cell('noday','&nbsp;') # day outside month
		if date.today() == date(self.year, self.month, day): # mark today
			body = '<a href="/FlightLog/add_sorties.html">%s</a>' %day
			return self.day_cell('today',body)
		if date(self.year,self.month,day) in self.done_sorties: # mark a day with a done flight
			body = '<a href="/FlightLog/delete_from_db?date=%d-%02d-%02d">%s</a>'  % (self.year,self.month,day,day)
			return self.day_cell('done',body)
		if date(self.year,self.month,day) in self.planned_sorties: # mark a day with a planned flight
			body = '<a href="/FlightLog/delete_from_db?date=%d-%02d-%02d">%s</a>'  % (self.year,self.month,day,day)
			return self.day_cell('planned',body)
		else: # a non-special month day
			body = '<a href="/FlightLog/calendar_add?date=%d-%02d-%02d">%s</a>' % (self.year,self.month,day,day)
			return self.day_cell('free',body)
			
	def formatmonth(self, year, month):
		self.year, self.month = year, month
		return super(MyHTMLCalendar, self).formatmonth(year, month)

	def day_cell(self, cssclass, body):
		return '<td class="%s">%s</td>' % (cssclass, body)