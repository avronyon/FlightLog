# coding=UTF-8
from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar']
CALENDAR_ID = open('calendarID.txt').readline()


def setup_service():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)
    return service


def create_event(e_summary,e_description,date,attendees):
    service = setup_service()
    # Refer to the Python quickstart on how to setup the environment:
    # https://developers.google.com/google-apps/calendar/quickstart/python
    # Change the scope to 'https://www.googleapis.com/auth/calendar' and delete any
    # stored credentials.

    event = {
        'summary': e_summary,
        'description': e_description,
        'start': {
            'date': date,
        },
        'end': {
            'date': date,
        },
        'attendees': [
            {'email': attendees},
        ],
    }

    event = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
    print('Event created: %s' % (event.get('iCalUID').split('@')[0]))
    return event.get('iCalUID').split('@')[0]

def delete_event(iCalUID):
    service = setup_service()
    service.events().delete(calendarId=CALENDAR_ID, eventId=iCalUID).execute()
    print('Event deleted successfully')
    return

def main():
    """Shows basic usage of the Google Calendar API.

    Creates a Google Calendar API service object and outputs a list of the next
    10 events on the user's calendar.
    """

    create_event('הצח','2 מטסים','2019-07-01','yonatan.avron@gmail.com')
    #delete_event('1j06fcr8apjtmgbu9vm1abahs8')
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time

if __name__ == '__main__':
    main()