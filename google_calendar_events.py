# coding=utf-8

from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import TokenExpiredError
from flask import request, redirect, session
from qikspace.api import utils, app, db, models
import time
import requests
import urllib.parse
from datetime import datetime
import json, webbrowser, _thread, os

client_email = "227928240833-4h7oa2v2esavo895d7dnrif5enuatm6k@developer.gserviceaccount.com"
client_id = "227928240833-nr1e437ql447ivd0p28ea249p4v4kk2v.apps.googleusercontent.com"
client_secret = "pqu7-Z808DDz-hLFFx0IUij8"
api_key = "AIzaSyA48ArmuqKusx8Di7LxcuzxGAPbtQhDbW0"

insert_request_url = "https://www.googleapis.com/calendar/v3/calendars/%s/events"# % calendar_id
quickadd_request_url = "https://www.googleapis.com/calendar/v3/calendars/%s/events/quickAdd"
base_scope = "https://www.googleapis.com/auth/calendar"
drive_scope = 'https://www.googleapis.com/auth/drive'
scope = [base_scope, drive_scope]
token_url = "https://accounts.google.com/o/oauth2/token"
authorization_base_url = "https://accounts.google.com/o/oauth2/auth"
redirect_uri = 'http://qikspace.com:48220/extensions/google/callback'
private_key_password='notasecret'
file_path = "root/"
location = None
google_token = None
refresh_token = None
test_calendar_id = "pjn81rsstvjbesvnjdaojklb4s@group.calendar.google.com"
test_event_id = "ep1i6a0gk5te0ccjiv613n8rig"


class Color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

google = OAuth2Session(client_id, scope=scope, redirect_uri=redirect_uri)

authorization_url, state = \
    google.authorization_url(authorization_base_url,
                             access_type="offline",
                             approval_prompt="force")


#session['oauth_state'] = state
#redirect(authorization_url)
webbrowser.open_new_tab(authorization_url)


@app.route("/extensions/google/callback")
def callback():
    print_in_color("redirected!", Color.BOLD)
    response_code = request.args['code']
    global google_token, refresh_token
    google_token_response = \
        google.fetch_token(token_url,
                           client_secret=client_secret,
                           code=response_code)
    google_token = google_token_response.get('access_token')
    refresh_token = google_token_response.get('refresh_token')

    #print("\n" + color.BLUE + str(token) + color.END+"\n")

    if google_token is not None:
        #list_calenders(google)
         body = {'summary': 'Updated by Qikspace',
            'location': '3nd Ave NE & Madison St',
            'start': {
                'dateTime': '2014-07-02T10:00:00.000-07:00'
            },
            'end': {
                'dateTime': '2014-07-02T10:25:00.000-07:00'
            }
           }

    #insert_simple_event(google, test_calendar_id, body)
    #update_event(google, test_calendar_id, test_event_id, body)
    delete_(google, test_calendar_id)
    #insert_calender(google, "qikspace")
    return "<center><h1>Calendar - It worked</h1></center>"


def list_calenders(session):
    url = 'https://www.googleapis.com/calendar/v3/users/me/calendarList'
    response = session.request('GET', url)
    s = "pjn81rsstvjbesvnjdaojklb4s@group.calendar.google.com"
    print_in_color(response.json()['items'][0]['id'])
    pass


def insert_simple_event(session, cal_id, info_dict):
    insert_url = 'https://www.googleapis.com/calendar/v3/calendars/%s/events' % cal_id
    header = {'Content-Type': 'application/json'}
    r = session.request('POST', insert_url, headers=header, data=json.dumps(info_dict))
    # TODO save r.get('id') evnet id
    print_in_color(r.text)


def update_event(session, cal_id, event_id, update_dict):
    update_url = 'https://www.googleapis.com/calendar/v3/calendars/%s/events/%s' % (cal_id, event_id)
    header = {'Content-Type': 'application/json'}
    r = session.request('PUT', update_url, headers=header, data=json.dumps(update_dict))
    print_in_color(r.text)


def delete_(session, cal_id, event_id=None):
    delete_calendar_url = 'https://www.googleapis.com/calendar/v3/calendars/%s' % cal_id
    delete_event_url = 'https://www.googleapis.com/calendar/v3/calendars/%s/events/%s' % (cal_id, event_id)
    delete_url = delete_event_url if event_id else delete_calendar_url
    r = session.request("DELETE", delete_url)
    print_in_color(r.status_code)
    print_in_color(r.text)


def insert_calender(session, tittle):
    insert_url = 'https://www.googleapis.com/calendar/v3/calendars'
    headers = {'Content-Type': 'application/json'}
    body = {'summary': tittle}
    r = session.request("POST", insert_url, headers=headers, data=json.dumps(body))
    print_in_color(r.text)
    print_in_color(r.json().get('id'))

    save = "igt4laiq0obr11n8vitk1b7jdo@group.calendar.google.com"


def update_calender(session, cid, update_dict):
    insert_url = 'https://www.googleapis.com/calendar/v3/calendars/%s' % cid
    headers = {'Content-Type': 'application/json'}
    r = session.request("PUT", insert_url, headers=headers, data=json.dumps(update_dict))
    print_in_color(r.text)
    print_in_color(r.json().get('id'))

    save = "igt4laiq0obr11n8vitk1b7jdo@group.calendar.google.com"


def print_in_color(text, color=Color.CYAN):
    print(color + str(text) + Color.END)


app.run('0.0.0.0', 48220, debug=True, threaded=True,
        use_debugger=False, use_reloader=False)