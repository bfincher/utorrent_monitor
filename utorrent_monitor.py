#!/usr/bin/python
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
import django
django.setup()

from data.models import CompletedTorrents
from datetime import datetime
from datetime import timedelta
from email.mime.text import MIMEText
import logging
from logging import DEBUG
import json
import smtplib
from utorrent_client import UtorrentClient

REQUIRED_COMPLETION_TIME = timedelta(seconds=30 * 60) # 30 minutes
logger = logging.getLogger('django_monitor')

class UtorrentMonitor(object):

    def __init__(self, settings):

        self.client = UtorrentClient(settings['utorrent_hostname'], settings['utorrent_username'], settings['utorrent_password'])
        self.labelsToDelete = settings['labels_to_delete']
        self.statusToDelete = settings['status_to_delete']
        self.autoDeleteDelta = timedelta(minutes=settings['autoDeleteAfterSeedingMinutes'])

    def run(self):
        try:
            self.client.list()

            if not self.client.response:
                logger.warn('No data received from client')
                return
        
            #print 'response = %s' % self.client.response.text
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
                completedTime = datetime.fromtimestamp(entry[24])

                defaults={'name': title, 'status': status, 'label': label, 'emailed': False}
                entry, created = CompletedTorrents.objects.get_or_create(
                    hash=tHash,
                    defaults=defaults)

                saveRequired = False
                if created:
                    logger.info('Created DB entry.  %s, %s', tHash, title)

                if entry.status != status or entry.label != label:
                    entry.status = status
                    entry.label = label
                    saveRequired=True

                if status in ['Fnished', 'Seeding']:
                    if entry.startSeedingTime is None:
                        entry.startSeedingTime = completedTime
                        saveRequired=True

                    if not entry.emailed:
                        send_email(title)
                        entry.emailed = True
                        saveRequired=True
            
                if saveRequired:
                    entry.save()

                if (label in self.labelsToDelete and status in self.statusToDelete):
                    delta = now - completedTime
                    if (delta > REQUIRED_COMPLETION_TIME):
                        if logger.isEnabledFor(DEBUG):
                            logger.debug('%s %s %s %s %s %s %s', tHash, title, label, status, added, completedTime, delta.total_seconds())
                    
                        logger.info('deleting %s', title)
                        self.client.removeData(tHash)
                        logger.info('Deleting DB entry %s, %s', entry.hash, entry.name)
                        entry.delete()

            autoDeleteTime = now - self.autoDeleteDelta
            for entry in CompletedTorrents.objects.filter(status='Seeding').filter(label__in=settings['labels_to_delete']).filter(startSeedingTime__lte=autoDeleteTime):
                logger.info('Auto deleting %s, %s due to max seeding time', entry.name, entry.hash)
                self.client.removeData(entry.hash)
                entry.delete()

            #delete entris that are not in the current list of data from Utorrent
            for toDelete in CompletedTorrents.objects.exclude(hash__in=allHashes):
                logger.info('Deleting DB entry %s, %s', toDelete.hash, toDelete.name)
                toDelete.delete()
        except Exception as e:
            logger.exception(e)

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
    with open('settings.json', 'r') as f:
        settings = json.load(f)

    monitor = UtorrentMonitor(settings)
    monitor.run()
