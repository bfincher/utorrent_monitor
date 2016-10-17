#!/usr/bin/python
'''
Created on Oct 1, 2016

@author: bfincher
'''

from collections import OrderedDict
from generic_client import GenericClient
import logging
from logging import DEBUG
from requests.compat import urlencode, urljoin
from requests import Session
import re
import time

logger = logging.getLogger(__name__)

class UtorrentClient(GenericClient):

    def __init__(self, host, username, password):
        super(UtorrentClient, self).__init__('http://' + host + ':8080/gui/')
        self.username = username
        self.password = password
        self.last_time = time.time()
        self.session.auth = (self.username, self.password)
        self.auth = None

    def request(self, method="get", params=None):
        if time.time() > self.last_time + 1800 or not self.auth:
            self.last_time = time.time()
            self._get_auth()
            
            logger.debug('Requested a %s connection to url %s', method.upper(), self.url)
        
        if not self.auth:
            logger.error('Authentication Failed')
            return False
        
        if params:
            params.update({'token': self.auth})
        if not params:
            params = OrderedDict({'token': self.auth})
            
        super(UtorrentClient, self).request(method, params)
        
    def _get_auth(self):
        """
        Makes a request to the token url to get a CSRF token
        """
        try:
            self.response = self.session.get(urljoin(self.url, 'token.html'), verify=False)
            self.response.raise_for_status()
            self.auth = re.findall("<div.*?>(.*?)</", self.response.text)[0]
        except Exception, e:
            logger.exception(e)
            self.auth = None

        return self.auth
    
    def removeData(self, torrent_hash):
        params = OrderedDict({'action': 'removedatatorrent', 'hash': torrent_hash})
        self.request(params=params)

    def list(self):
        params = OrderedDict({'list': '1'})
        self.request(params=params)

