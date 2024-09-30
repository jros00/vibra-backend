from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Track(models.Model):
    track_id = models.IntegerField(unique=True)  # Unique track ID from Jamendo
    track_title = models.CharField(max_length=255)
    artist_name = models.CharField(max_length=255)
    album_id = models.IntegerField(unique=False)  # Unique track ID from Jamendo
    album_name = models.CharField(max_length=255, null=True, blank=True)
    album_image = models.URLField(max_length=500, null=True, blank=True)  # URL for album cover image
    album_image_palette = models.JSONField(null=True, blank=True)
    album_image_dominant_color = models.JSONField(null=True, blank=True)
    artist_id = models.IntegerField(unique=False)  # Unique track ID from Jamendo
    audio_url = models.URLField(max_length=500)  # URL to stream/download the audio file
    duration = models.PositiveIntegerField()  # Duration in seconds
    release_date = models.DateField(null=True, blank=True)
    genre = models.JSONField(null=True, blank=True)
    share_url = models.URLField(max_length=500, null=True, blank=True)  # URL to share the track
    license_url = models.URLField(max_length=500, null=True, blank=True)  # License for commercial use

    def __str__(self):
        return self.track_title
    
class AudioFeature(models.Model):
    track = models.OneToOneField(Track, on_delete=models.CASCADE)
    mfcc_mean = models.JSONField()  # Store MFCC as a JSON field
    tempo = models.FloatField()
    chroma_mean = models.JSONField(blank=True, null=True)  # Store chroma features as a JSON field

    def __str__(self):
        return f"Audio features for {self.track.track_title}"

    def __str__(self):
        return self.track_title

class UserActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    activity_type = models.CharField(max_length=100)  # the built-in user function can track loggin in and loggin (and time) out but not which content the user has interacted with
    timestamp = models.DateTimeField(default=timezone.now)
    description = models.TextField(null=True, blank=True)

class Artist(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=100)

    def __str__(self):
        return self.name
