#!/usr/bin/python
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

from email.mime.text import MIMEText
import json
from datetime import datetime
from datetime import timedelta
import smtplib
from utorrent_client import UtorrentClient
from data.models import *
from data.models import CompletedTorrents
import django

LABELS = {'tv'}
STATUS = {'Finished'}
REQUIRED_COMPLETION_TIME_SECONDS = 30 * 60 # 30 minutes
TWO_DAYS = timedelta(seconds=2)
#TWO_DAYS = timedelta(days=2)

class UtorrentMonitor(object):

    def __init__(self, host, username, password):

        self.client = UtorrentClient(host, username, password)

    def run(self):
        self.client.list()
        
        j = json.loads(self.client.response.text)

        now = datetime.now()
        twoDaysAgo = now - TWO_DAYS
        for entry in j['torrents']:
            tHash = entry[0]
            title = entry[2]
            label = entry[11]
            status = entry[21]
            #added = datetime.fromtimestamp(entry[23])
            completed = datetime.fromtimestamp(entry[24])

            if status == 'Finished' or status == 'Seeding':
                existing = CompletedTorrents.objects.filter(hash=tHash).first()
                if not existing:
                    existing = CompletedTorrents()
                    existing.hash = tHash
                    existing.name = title
                    existing.label = label
                    existing.emailed = False
                    existing.save()

                if not existing.emailed:
                    send_email(title)
                    existing.emailed = True
                    existing.save()
            
                if (label in LABELS and status in STATUS):
                    delta = now - completed
                    if (delta.total_seconds() > REQUIRED_COMPLETION_TIME_SECONDS):
                        #print '%s %s %s %s %s %s %s' % (tHash, title, label, status, added, completed, delta.total_seconds())
                    
                        print 'deleting %s' % title
                        self.client.removeData(tHash)
                        existing.deletedTime = now
                        existing.save()

        CompletedTorrents.objects.filter(label__in=LABELS, deletedTime__lt=twoDaysAgo).delete()

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
