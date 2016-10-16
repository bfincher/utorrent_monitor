#!/usr/bin/python
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

from data.models import CompletedTorrents
from datetime import datetime
from datetime import timedelta
import django
from email.mime.text import MIMEText
import logging
from logging import DEBUG
import json
import smtplib
from utorrent_client import UtorrentClient

LABELS_TO_DELETE = {'tv', 'Movies'}
STATUS_TO_DELETE = {'Finished'}
REQUIRED_COMPLETION_TIME = timedelta(seconds=30 * 60) # 30 minutes
logger = logging.getLogger('django_monitor')

TWO_DAYS = timedelta(days=2)

class UtorrentMonitor(object):

    def __init__(self, host, username, password):

        self.client = UtorrentClient(host, username, password)

    def run(self):
        self.client.list()
        
        j = json.loads(self.client.response.text)

        now = datetime.now()
        allHashes = []
        for entry in j['torrents']:
            tHash = entry[0]
            allHashes.append(tHash)
            title = entry[2]
            label = entry[11]
            status = entry[21]
            #added = datetime.fromtimestamp(entry[23])
            completed = datetime.fromtimestamp(entry[24])

            defaults={'name': title, 'status': status, 'label': label, 'emailed': False}
            entry, created = CompletedTorrents.objects.get_or_create(
                hash=tHash,
                defaults=defaults)

            if entry.status != status or entry.label != label:
                entry.status = status
                entry.label = label
                entry.save()

            if (not entry.emailed) and (status == 'Finished' or status == 'Seeding'):
                send_email(title)
                entry.emailed = True
                entry.save()
            
            if (label in LABELS_TO_DELETE and status in STATUS_TO_DELETE):
                delta = now - completed
                if (delta > REQUIRED_COMPLETION_TIME):
                    if logger.isEnabledFor(DEBUG):
                        logger.debug('%s %s %s %s %s %s %s', tHash, title, label, status, added, completed, delta.total_seconds())
                    
                    logger.info('deleting %s', title)
                    self.client.removeData(tHash)
                    entry.deletedTime = now
                    entry.save()

        twoDaysAgo = now - TWO_DAYS

        #delete DB entry for TV, Movies that have beel deleted from Utorrent more than 2 days ago
        CompletedTorrents.objects.filter(label__in=LABELS_TO_DELETE).filter(deletedTime__lt=twoDaysAgo).delete()

        #delete non TV, Movies that are not in the current list of data from Utorrent
        CompletedTorrents.objects.exclude(label__in=LABELS_TO_DELETE).exclude(hash__in=allHashes).delete()

        #delete TV, Movies that are not in the list from Utorrent and have a deletedTime of None
        CompletedTorrents.objects.filter(label__in=LABELS_TO_DELETE).filter(deletedTime=None).exclude(hash__in=allHashes).delete()

def send_email(content):
    msg = MIMEText('Torrent %s completed' % content)
    _from = 'brian@fincherhome.com'
    to = _from

    msg['Subject'] = 'Torrent %s completed' % content
    msg['From'] = _from
    msg['To'] = to

    s = smtplib.SMTP('localhost')
    s.sendmail(_from, [to], msg.as_string())
    s.quit()

if __name__ == '__main__':
        django.setup()
        monitor = UtorrentMonitor('uvmediavpn', 'admin', 'admin')
        monitor.run()
