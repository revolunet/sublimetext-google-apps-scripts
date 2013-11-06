# -*- encoding: UTF-8 -*-

import urllib
import httplib2
from oauth2client.client import OAuth2WebServerFlow, FlowExchangeError
from oauth2client.file import Storage

class GoogleOAuth2(object):
    ''' class to manage oauth flow easily and store credentials. refresh token is used if needed'''

    # depends on the token you need (online, offline, native, mobile...)
    # see https://developers.google.com/accounts/docs/OAuth2
    REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'
    ACCESS_TYPE = 'offline'

    # range of the authorisation on google services
    DEFAULT_SCOPE = 'https://www.googleapis.com/auth/drive'

    def __init__(self, client_id, client_secret, scope=None, store=None):
        if not scope:
            scope = self.DEFAULT_SCOPE
        self.scope = scope
        self.client_id = client_id
        self.client_secret = client_secret
        self._credentials = None
        self.flow = None
        self.storage = None
        if store:
            self.storage = Storage(store)

    def set_token(self, *args, **kwargs):
        ''' called by the oauth process when user submitted final token '''
        code = args[0]
        try:
            credentials = self.flow.step2_exchange(code)
        except FlowExchangeError:
            credentials = None
        if credentials and self.storage:
            self.storage.put(credentials)
        return credentials

    def ask_code(self, authorize_url, callback):
        ''' default oauth process : use console only '''
        print("open %s in your browser and paste the code below" % authorize_url)
        code = raw_input('Enter verification code: ').strip()
        return callback(code)

    def get_credentials(self, force=False, callback=None):
        ''' start the oauth process. refresh token if expired and refreshable. '''
        if not callback:
            callback = self.ask_code

        credentials = None
        if self.storage:
            credentials = self.storage.get()
        if credentials and credentials.access_token_expired and credentials.refresh_token:
            # refresh existing expired token
            http = httplib2.Http()
            http = credentials.authorize(http)
            credentials.refresh(http)

        if force or not credentials:
            self.flow = OAuth2WebServerFlow(self.client_id, self.client_secret, self.scope, self.REDIRECT_URI, access_type=self.ACCESS_TYPE)
            authorize_url = urllib.unquote(self.flow.step1_get_authorize_url())
            return callback(authorize_url, self.set_token)

        return credentials

    def get_token(self, force=False, callback=None):
        creds = self.get_credentials(force=force, callback=callback)
        if creds:
            return creds.token_response.get('access_token')
        return None

if __name__=='__main__':
    # customize with your secrets here
    CLIENT_ID = "1058459624870.apps.googleusercontent.com"
    CLIENT_SECRET = "VDfezc8MADUbEBCZ3Wo_nyV8"
    auth = GoogleOAuth2(CLIENT_ID, CLIENT_SECRET)
    token = auth.get_token()
    if token:
        print "SUCCESS, access_token:", token
    else:
        print "FAILED AUTH!"
    
