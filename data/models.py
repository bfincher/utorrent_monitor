from django.db import models

class CompletedTorrents(models.Model):
    hash = models.CharField(max_length=40, primary_key=True)
    name = models.CharField(max_length=255)
    label = models.CharField(max_length=20, blank=True)
    status = models.CharField(max_length=20)
    emailed = models.BooleanField(default=False)
    startSeedingTime = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return 'hash = %s, name = %s, label = %s, status = %s, emailed = %s' % (self.hash, self.name, self.label, self.status, self.emailed)
