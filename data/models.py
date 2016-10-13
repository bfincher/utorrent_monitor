from django.db import models

class CompletedTorrents(models.Model):
    hash = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    label = models.CharField(max_length=20, blank=True)
    status = models.CharField(max_length=20)
    emailed = models.BooleanField(default=False)
    deletedTime = models.DateTimeField(null=True)

    def __str__(self):
        return 'hash = %s, name = %s, label = %s, status = %s, emailed = %s, deletedTime = %s' % (self.hash, self.name, self.label, self.status, self.emailed, self.deletedTime)
