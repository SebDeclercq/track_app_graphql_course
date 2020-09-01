from django.db import models


class Track(models.Model):
    title: models.CharField = models.CharField(max_length=50)
    description: models.TextField = models.TextField()
    url: models.URLField = models.URLField()
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)
