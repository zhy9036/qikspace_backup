# coding=utf-8

from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import TokenExpiredError
from flask import request, redirect, session
from qikspace.api import utils, app, db, models
import time
import requests
import urllib.parse
import json, webbrowser, _thread, os

#google event insert URL: POST https://www.googleapis.com/calendar/v3/calendars/{*calendarId}/events

client_email = "227928240833-4h7oa2v2esavo895d7dnrif5enuatm6k@developer.gserviceaccount.com"
client_id = "227928240833-nr1e437ql447ivd0p28ea249p4v4kk2v.apps.googleusercontent.com"
client_secret = "pqu7-Z808DDz-hLFFx0IUij8"
api_key = "AIzaSyA48ArmuqKusx8Di7LxcuzxGAPbtQhDbW0"

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
#print("\n" + color.YELLOW + google_token + color.END+"\n")
#print ("GO HERE", authorization_url)


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
        '''_thread.start_new_thread(create_new_file, ("/home/yang/Desktop/test1.txt",))
        _thread.start_new_thread(create_new_file, ("/home/yang/Desktop/test2.txt",))
        _thread.start_new_thread(create_new_file, ("/home/yang/Desktop/test3.txt",))'''

        #create_new_file("/home/yang/Desktop/test2.txt")
        #upload_large_file("/home/yang/Desktop/test2.txt", "text/plain")
        #_list_children(google, 'root')
        #_create_folder(google, 'nimaa')
        #_detected_changes(google)
        #_remove_file_id('0B97wiYIuSN6uQUNZcmRHY2Vrdzg')
        #delete_items_by_id(google, ['0B97wiYIuSN6uQUNZcmRHY2Vrdzg',
        #                            '0B97wiYIuSN6ueHFxZlgzdkdHUms'])
        #_trash_single_item(google, '0B97wiYIuSN6uRVpBVkwyaFgxaFE', False)
        download_single_file(google, '0B97wiYIuSN6uZ0NxUWVHVFpXMk0')

    return "<center><h1>It worked</h1></center>"

"""
#######################################
# PART I:
#   CREATE ITEMS (file, folder)
#
#######################################
"""

def _create_folder(session, folder_name, parent_id="root"):
    cf_url = 'https://www.googleapis.com/drive/v2/files'
    cf_headers = {'Content-Type': 'application/json'}
    cf_body = {'title': folder_name, 'parents': [{'id': parent_id}],
               'mimeType': "application/vnd.google-apps.folder"}
    cf_response = session.post(cf_url, headers=cf_headers, data=json.dumps(cf_body))
    fid = cf_response.json()['id']
    #print_in_color(cf_response.json()['id'], Color.PURPLE)
    _record_file_id(folder_name, fid)


def create_new_file(origin_path):
    URL = "https://www.googleapis.com/upload/drive/v2/files?" \
          + urllib.parse.urlencode({'key': api_key, 'convert': True, 'uploadType': "multipart"})
    oauth_google = OAuth2Session(client_id, token={'access_token': google_token,
                                                   'token_type': 'bearer'})
    #print("\n" + color.YELLOW + str(oauth_google) + color.END+"\n")
    #req_body_dict = {"uploadType": "media",
    #                 "file": (origin_path, open(origin_path, 'rb'))}
    #req_body = json.dumps(req_body_dict)

    try:
        meta_dict = {"title": origin_path.split('/')[-1], "description": 'haha haha haha'}
        headers = {'Authorization': 'Bearer {}'.format(google_token)}
        data = ('metadata', json.dumps(meta_dict), 'application/json; charset=UTF-8')
        #with open(origin_path, 'rb') as f:

        file = (origin_path, open(origin_path, 'rb'), 'text/plain')
        files = {'data': data, 'file': file}

        response = oauth_google.post(URL, headers=headers, files=files)

        print_in_color(response.text)
        #print_in_color(response.request.__dict__)

        '''action_response = oauth_google.request(
            "POST", URL, files={'file': ('test.txt', open(origin_path, 'rb'), 'text/plain; charset=UTf-8')})
        #print(action_response.request.__dict__)
        print_in_color(action_response, Color.YELLOW)
        print_in_color(action_response.text)'''
    except TokenExpiredError:
        token = oauth_google.refresh_token(token_url, refresh_token,
                                           client_id=client_id,
                                           client_secret=client_secret)


def upload_large_file(origin_path, file_type, parent_id="root"):
    """

    :param origin_path:
    :param file_type:
    :param parent_id:
    """
    oauth_google = OAuth2Session(client_id, token={'access_token': google_token,
                                                   'token_type': 'bearer'})
    file_name = origin_path.split('/')[-1]
    # STEP1: Start a resumable session
    # if successed, STEP2: save 'Location'
    url_step1 = "https://www.googleapis.com/upload/drive/v2/files?uploadType=resumable"
    first_headers = {'X-Upload-Content-Type': file_type,
                     'Content-Length': '38',
                     'Content-Type': 'application/json; charset=UTF-8',
                     'Authorization': 'Bearer {}'.format(google_token)}
    meta_body_dict = {"title": file_name, "description": 'haha haha haha',
                      "parents": [{'id': parent_id}]}

    try:
        response_1 = oauth_google.post(url_step1, headers=first_headers,
                                       data=json.dumps(meta_body_dict))

        print_in_color(response_1, Color.PURPLE)
        print_in_color(response_1.headers, Color.BLUE)
        if response_1.status_code == 200:
            global location
            location = response_1.headers.get('Location')

    except TokenExpiredError:
        refreshed_token = oauth_google.refresh_token(token_url, refresh_token,
                                                     client_id=client_id,
                                                     client_secret=client_secret)

    # STEP3:
    file_length = os.path.getsize(origin_path)
    put_headers = {'Content-Length': file_length,
                   'Content-Type': file_type,
                   }
    #file = (origin_path, open(origin_path, 'rb'), 'text/plain')
    #files = {'file': file}
    #f = open(origin_path, 'rb')
    try:
        response_3 = oauth_google.put(location, headers=put_headers, data=open(origin_path, 'rb'))
        print_in_color(response_3.status_code, Color.GREEN)
        print_in_color(response_3.json(), Color.BLUE)
        fid = response_3.json()['id']
        #print_in_color(cf_response.json()['id'], Color.PURPLE)
        _record_file_id(file_name, fid)
    except TokenExpiredError:
        refreshed_token = oauth_google.refresh_token(token_url, refresh_token,
                                                     client_id=client_id,
                                                     client_secret=client_secret)

    # Check if upload the file successfully
    # If not, should use EX Back off to retry
    # TODO Apply Ex Back-Off

    flag_status = response_3.status_code
    i = 0
    while flag_status not in [200, 201]:
        i += 1
        if i > 5:
            break
        time.sleep(2 ** i)
        # Request the status
        status_headers = {'Content-Length': '0',
                          'Content-Range': '*/' + str(file_length),
                          'Authorization': 'Bearer {}'.format(google_token)}
        status_response = oauth_google.put(location, headers=status_headers)
        print_in_color(status_response, Color.RED)
        #print_in_color(status_response.text, Color.BLUE)
        flag_status = status_response.status_code
        if flag_status not in [200, 201]:
            finished = int(status_response.json()['Range'].split("-")[1]) + 1
            remined = file_length - finished
            put_headers.update({'Content-Length': remined,
                                'Content_Range': str(finished) + "/" + str(file_length)})

            # chop the file
            f = open(origin_path, 'rb')
            f.read(finished)
            remined_file = f.read(remined)

            try:
                retried_response = \
                    oauth_google.put(location, headers=put_headers,
                                     data=remined_file)
                flag_status = retried_response.status_code

            except TokenExpiredError:
                refreshed_token = \
                    oauth_google.refresh_token(token_url, refresh_token,
                                               client_id=client_id,
                                               client_secret=client_secret)


def _record_file_id(name, fid):
    f = open('/home/yang/Desktop/ids', 'a')
    f.write('\n%s:::%s' % (fid, name))
    f.close()


"""
#######################################
# PART II:
#   DELETE, TRASH, UNTRASH
#   (files, folders)
#######################################
"""

def _remove_file_id(fid):
    f = open('/home/yang/Desktop/ids', 'r')
    lines = f.readlines()
    f.close()
    f = open('/home/yang/Desktop/ids', 'w')
    for line in lines:
        if line.split(':::')[0] != fid:
            f.write(line)
    f.close()

def delete_items_by_id(session, ids):
    """

    :param session:
    :param ids:
    """

    for fid in ids:
        _thread.start_new_thread(_delete_single_item, (session, fid))


def _delete_single_item(session, fid):
    del_url = "https://www.googleapis.com/drive/v2/files/%s"
    code, tries = 0, 0
    while code != 200:
        if tries > 6:
            break
        time.sleep(2 ** tries)
        code = session.request("DELETE", del_url % fid).status_code
        if code == 200:
            _remove_file_id(fid)
        tries += 1


def trash_items_by_id(session, ids, trash_mode=True):
    """

    :param session:
    :param ids:
    :param trash_mode:
    """

    for fid in ids:
        _thread.start_new_thread(_trash_single_item, (session, fid, trash_mode))


def _trash_single_item(session, fid, trash_mode=True):
    mode_str = "trash" if trash_mode else "untrash"
    trash_url = "https://www.googleapis.com/drive/v2/files/%s/" + mode_str
    tries, code = 0, 0
    while code != 200:
        if tries > 6:
            break
        time.sleep(2 ** tries)
        code = session.request("POST", trash_url % fid).status_code
        tries += 1

"""
#######################################
# PART III:
#   DOWNLOAD
#   (files, folders)
#######################################
"""


def download_single_file(session, fid):
    """

    :param session:
    :param fid:
    """
    # STEP 1: Fetch download url
    url_fetch = 'https://www.googleapis.com/drive/v2/files/%s' % fid
    url_download = session.request('GET', url_fetch).json()['downloadUrl']

    # STEP 2: Download file
    download_response = session.request('GET', url_download)
    with open("/home/yang/Desktop/" + fid, 'wb') as f:
        for chunk in download_response.iter_content(256 * 1024):
            f.write(chunk)
    print_in_color(download_response.text)


def _list_children(session, parent):
    list_url = "https://www.googleapis.com/drive/v2/files/%s/children" % parent
    list_response = session.get(list_url)
    print_in_color(list_response.text, Color.BOLD)


def print_in_color(text, color=Color.CYAN):
    print(color + str(text) + Color.END)


def _detected_changes(session, largestChangeId):
    #info_response = session.get('https://www.googleapis.com/drive/v2/about')
    #largeChangeId_plus = int(info_response.json()['largestChangeId'])
    changes_response = session.get('https://www.googleapis.com'
                                   '/drive/v2/changes?pageToken=%d' % largestChangeId)
    print_in_color(changes_response.text)


#_thread.start_new_thread(app.run, ('0.0.0.0', 48220), {'debug':True, 'threaded':True, 'use_debugger':False, 'use_reloader':False})

app.run('0.0.0.0', 48220, debug=True, threaded=True,
        use_debugger=False, use_reloader=False)