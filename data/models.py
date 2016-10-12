from django.db import models

class CompletedTorrents(models.Model):
    hash = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    label = models.CharField(max_length=20, blank=True)
    emailed = models.BooleanField(default=False)
    deletedTime = models.DateTimeField(null=True)
