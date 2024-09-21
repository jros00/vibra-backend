from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

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
