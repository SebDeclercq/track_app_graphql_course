from django.db import models
from django.contrib.auth import get_user_model


class Track(models.Model):
    title: models.CharField = models.CharField(max_length=50)
    description: models.TextField = models.TextField()
    url: models.URLField = models.URLField()
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    posted_by: models.ForeignKey = models.ForeignKey(
        get_user_model(), null=True, on_delete=models.CASCADE
    )


class Like(models.Model):
    user: models.ForeignKey = models.ForeignKey(
        get_user_model(), related_name='likes', on_delete=models.CASCADE
    )
    track: models.ForeignKey = models.ForeignKey(
        Track, related_name='likes', on_delete=models.CASCADE
    )
