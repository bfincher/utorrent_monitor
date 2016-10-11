#!/usr/bin/python
'''
Created on Oct 1, 2016

@author: bfincher
'''

from collections import OrderedDict
from requests.compat import urlencode, urljoin
from requests import Session
import re
import time
import traceback

class UtorrentClient(object):

    def __init__(self, host, username, password):
        self.username = username
        self.password = password
        self.host = host
        self.url = "http://" + self.host + ":8080/gui/"
        self.last_time = time.time()
        self.response = None
        self.auth = None
        self.session = make_session()
        self.session.auth = (self.username, self.password)

    def request(self, method="get", params=None):
        log_string = ''
        if time.time() > self.last_time + 1800 or not self.auth:
            self.last_time = time.time()
            self._get_auth()
            
            log_string = 'Requested a {0} connection to url {1}'.format(method.upper(), self.url)
        
        if not self.auth:
            print 'Authentication Failed'
            return False
        
        if params:
            params.update({'token': self.auth})
        if not params:
            params = OrderedDict({'token': self.auth})
            
        if params:
            log_string += '?%s' % urlencode(params)
            
        #print log_string
        
        try:
            self.response = self.session.request(method, 
                                                 self.url, 
                                                 params=params, 
                                                 data=None, 
                                                 timeout=120, 
                                                 verify=False)
            self.response.raise_for_status()
        except Exception:
            traceback.print_exc()
            return False
        
    def _get_auth(self):
        """
        Makes a request to the token url to get a CSRF token
        """
        try:
            self.response = self.session.get(urljoin(self.url, 'token.html'), verify=False)
            self.response.raise_for_status()
            self.auth = re.findall("<div.*?>(.*?)</", self.response.text)[0]
        except Exception:
            traceback.print_exc()
            self.auth = None

        return self.auth
    
    def removeData(self, torrent_hash):
        params = OrderedDict({'action': 'removedata', 'hash': torrent_hash})
        self.request(params=params)

    def list(self):
        params = OrderedDict({'list': '1'})
        self.request(params=params)

def make_session():
    session = Session()
    return session

