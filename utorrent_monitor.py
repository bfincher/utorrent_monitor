#!/usr/bin/python
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

from email.mime.text import MIMEText
import json
from datetime import datetime
import smtplib
from utorrent_client import UtorrentClient
from data.models import *
from data.models import CompletedTorrents
import django

LABELS = {'tv'}
STATUS = {'Finished'}
REQUIRED_COMPLETION_TIME_SECONDS = 30 * 60 # 30 minutes

class UtorrentMonitor(object):

    def __init__(self, host, username, password):

        self.client = UtorrentClient(host, username, password)

    def run(self):
        self.client.list()
        
        j = json.loads(self.client.response.text)

        print j
        
        now = datetime.now()
        all_hashes = []
        for entry in j['torrents']:
            tHash = entry[0]
            title = entry[2]
            label = entry[11]
            status = entry[21]
            #added = datetime.fromtimestamp(entry[23])
            completed = datetime.fromtimestamp(entry[24])

            if status == 'Finished' or status == 'Seeding':
                all_hashes.append(tHash)
                if not CompletedTorrents.objects.filter(hash=tHash).first():
                    send_email(title)
                    o = CompletedTorrents()
                    o.hash = tHash
                    o.name = title
                    o.save()
            
            if (label in LABELS and status in STATUS):
                delta = now - completed
                if (delta.total_seconds() > REQUIRED_COMPLETION_TIME_SECONDS):
                    #print '%s %s %s %s %s %s %s' % (tHash, title, label, status, added, completed, delta.total_seconds())
                    
                    print 'deleting %s' % title
                    self.client.removeData(tHash)

        if all_hashes:
            CompletedTorrents.objects.exclude(hash__in=all_hashes).delete()

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
