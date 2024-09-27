from django.db import models
from django.contrib.auth.models import User
from core.models import Track
from django.utils import timezone

class UserPreference(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    track = models.ForeignKey(Track, on_delete=models.CASCADE)
    preference = models.CharField(max_length=10)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'track')  # Ensures that each user can have only one preference per track


class GlobalPreference(models.Model):
    track = models.OneToOneField(Track, on_delete=models.CASCADE)
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)
    

class ListeningHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=timezone.now)
    track = models.ForeignKey(Track, on_delete=models.CASCADE)
    listening_time = models.DurationField(null=True, blank=True)
