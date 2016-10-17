import logging
from logging import DEBUG
from requests import Session
from requests.compat import urlencode

logger = logging.getLogger(__name__)

class GenericClient(object):

    def __init__(self, url):
        self.url = url
        self.response = None
        self.make_session()

    def request(self, method="get", params=None):
        if params:
            logger.debug('?%s',urlencode(params))

        try:
            self.response = self.session.request(method, 
                                                 self.url, 
                                                 params=params, 
                                                 data=None, 
                                                 timeout=120, 
                                                 verify=False)
            self.response.raise_for_status()
        except Exception, e:
            logger.exception(e)
            return False

    def make_session(self):
        self.session = Session()
