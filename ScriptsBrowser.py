# -*- encoding: UTF-8 -*-

"""
ScriptsBrowser.py - https://github.com/revolunet/sublimetext-google-apps-scripts
copyright: (c) 2013 by Julien Bouquillon - julien@revolunet.com
license: MIT
"""

import sys
import os
# force include 3rd party libs
LIBS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lib')
sys.path.insert(0, LIBS_PATH)



import json
import requests
import GoogleOAuth2
import SublimeHelper

class GoogleAppsScriptsBrowser(object):
    ''' helper to make import/export calls to the Google Drive API using the python-requests library '''

    def __init__(self, client_id, client_secret, creds_storage=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.creds_storage = creds_storage
        self.scope = 'https://www.googleapis.com/auth/drive https://www.googleapis.com/auth/drive.scripts'
        self.token = None
        self.login_errors =0
        self.oauth_token_callback = None

    def login(self, force=False):
        if self.login_errors > 10:
            raise Exception('too many login errors')
        auth = GoogleOAuth2.GoogleOAuth2(client_id=self.client_id, client_secret=self.client_secret, scope=self.scope, store=self.creds_storage)
        self.token = auth.get_token(force=force, callback=self.oauth_token_callback)
        self.login_errors += 1

    def _get_headers(self):
        return {
            'Authorization': 'Bearer %s' % self.token
        }

    def set_token_flow_callback(self, callback):
        self.oauth_token_callback = callback

    def _request(self, url, method='get', data=None, headers=None):
        if not self.token:
            #SublimeHelper.message('Please login and try again')
            #self.login(force=True)
            return
            # replay
            #return self._request(url, method=method, data=data)
        all_headers = self._get_headers()
        if headers:
            all_headers.update(headers)

        result = getattr(requests, method)(url, data=data, headers=all_headers)
        if result.status_code == 201:
            return result.json()
        elif result.json().has_key('error'):
            data= result.json()
            if data.get('error', {}).get('code') == 401:
                SublimeHelper.message('ERROR 401, please restart auth process : %s' % data.get('error', {}).get('message'))
            else:
                SublimeHelper.message('ERROR : %s' % data.get('error', {}).get('message'))
            # replay
            #return self._request(url, method=method, data=data)
        else:
            return result.json()
        raise Exception('error calling %s' % url)

    def projects(self):
        url = "https://www.googleapis.com/drive/v2/files?q=mimeType='application/vnd.google-apps.script'"
        projects = self._request(url)
        if projects:
            return projects.get('items', [])
        return []

    def files(self, id):
        url = "https://script.google.com/feeds/download/export?id=%s&format=json" % id
        return self._request(url).get('files', [])

    def update_file(self, project_id, file_id, contents):
        files = self.files(project_id)
        for file in files:
            if file.get('id')==file_id:
                file['source'] = contents
        url = "https://www.googleapis.com/upload/drive/v2/files/%s" % project_id
        headers = {
            'Content-Type': 'application/vnd.google-apps.script+json'
        }
        result = self._request(url, method='put', data=json.dumps({'files':files}), headers=headers)
        return not result.has_key('error')
