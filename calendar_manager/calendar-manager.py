	# coding=UTF-8

import sqlite3, argparse
from google_api_quickstart import create_event, delete_event

DJANGO_DB_PATH = 'ERROR NO DB PATH SUBMITTED'

def get_row(iCalUID):
	con = sqlite3.connect(DJANGO_DB_PATH,timeout = 1)
	cur = con.cursor()
	query = """SELECT dt,day_value,night_value,gnd_activity,email
			from FlightLog_plannedflight as a join auth_user as b
			on a.pilot=b.id where ICalUID = '""" + iCalUID +"'"
	cur.execute(query)
	ans = cur.fetchall()
	assert(len(ans)==1) #something went wrong if there is not one answer
	row = ans[0]
	date = row[0]
	e_summery = ''.encode('UTF-8')
	if not row[1] == 0:
		e_summery +=  'הצח יום '
	if not row[2] == 0:
		e_summery += 'לילה '
	if not row[3] == None:
		e_summery += row[3].encode('UTF-8')
	email = row[4]
	e_summery = e_summery.replace('gnd_','').replace('konan','כונן').replace('yarpa','ירפא').replace('malam','מלאמ').replace('sim','סימולטור')
	e_description = e_summery
	return e_summery, e_description, date , email
	
def change_iCalUID(new_iCalUID, old_iCalUID):
	con = sqlite3.connect(DJANGO_DB_PATH,timeout = 1)
	cur = con.cursor()
	query = "UPDATE FlightLog_plannedflight SET iCalUID ='"+new_iCalUID+"'"+" WHERE iCalUID ='"+old_iCalUID+"'"
	cur.execute(query)
	con.commit()
	
def add_to_calendar(old_iCalUID):
	e_summery,e_description,date,email = get_row(old_iCalUID)
	new_iCalUID = create_event(e_summery,e_description,date,email)
	change_iCalUID(new_iCalUID, old_iCalUID)
	
def get_an_unsynced_iCalUID():
	con = sqlite3.connect(DJANGO_DB_PATH,timeout = 1)
	cur = con.cursor()
	query = """SELECT iCalUID
			from FlightLog_plannedflight where ICalUID like 'UNSYNCED%' and dt > DATE() """
	cur.execute(query)
	ans = cur.fetchone()
	return ans[0]
	

def main():
	global DJANGO_DB_PATH
	parser = argparse.ArgumentParser(description='Manage google calendar events')
	parser.add_argument('--sqliteDB', nargs=1, required=True)
	group = parser.add_mutually_exclusive_group(required=True)
	group.add_argument('--add', nargs=1)
	group.add_argument('--delete', nargs=1)
	args =  parser.parse_args()
	DJANGO_DB_PATH = args.sqliteDB[0]
	if not args.add == None:
		add_to_calendar(args.add[0])
	if not args.delete == None:
		delete_event(args.delete[0])
	##flush all unsynced to DB
	while(True):
		try:
			uid = get_an_unsynced_iCalUID()
			add_to_calendar(uid)
		except:
			break

if __name__ == '__main__':
    main()