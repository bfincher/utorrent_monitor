from django.db import models

class CompletedTorrents(models.Model):
    hash = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
