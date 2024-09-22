from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
class Track(models.Model):
    track_id = models.CharField(max_length=255, unique=True)  # Unique track ID from Jamendo
    track_title = models.CharField(max_length=255)
    artist_name = models.CharField(max_length=255)
    album_name = models.CharField(max_length=255, null=True, blank=True)
    album_image = models.URLField(max_length=500, null=True, blank=True)  # URL for album cover image
    audio_url = models.URLField(max_length=500)  # URL to stream/download the audio file
    duration = models.PositiveIntegerField()  # Duration in seconds
    release_date = models.DateField(null=True, blank=True)
    genre = models.CharField(max_length=255, null=True, blank=True)
    share_url = models.URLField(max_length=500, null=True, blank=True)  # URL to share the track
    pro_license = models.URLField(max_length=500, null=True, blank=True)  # License for commercial use

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

class Song(models.Model):
    # Metadata Fields
    clip_id = models.IntegerField(unique=True, default=0)
    track_number = models.CharField(max_length=10, default='0')
    title = models.CharField(max_length=255, default='Unknown Title')
    artist = models.CharField(max_length=255, default='Unknown Artist')
    album = models.CharField(max_length=255, null=True, blank=True, default='Unknown Album')
    url = models.URLField(default='http://example.com') # Refers to an artist or album page
    segment_start = models.IntegerField(default=0)
    segment_end = models.IntegerField(default=0)
    original_url = models.URLField(default='http://example.com') # Direct link to the specific audio clip
    mp3_path = models.CharField(max_length=500, default='Unknown Path')

    # Simple tags as a ManyToManyField
    tags = models.ManyToManyField('Tag')

    def __str__(self):
        return f"{self.artist} - {self.title}"
class Tag(models.Model):
    name = models.CharField(max_length=100, default='Unknown Tag')
    votes = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name} ({self.votes} votes)"
class VisualContent(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='visual_content/')
    mood = models.CharField(max_length=50)  # Optional if content depends on mood
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    published_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title

class ContentView(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.ForeignKey(VisualContent, on_delete=models.CASCADE)  # or any content model
    timestamp = models.DateTimeField(default=timezone.now)

class SongView(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    song = models.ForeignKey(Song, on_delete=models.CASCADE)  # or any content model
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.user.username} viewed {self.content.title} on {self.timestamp}'
