from django.db import models
from django.utils import timezone


class User(models.Model):
    name = models.CharField(max_length=50)
    
    def __str__(self):
        return self.name

class UserActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    activity_type = models.CharField(max_length=100)  # e.g., 'login', 'logout', 'view_page'
    timestamp = models.DateTimeField(default=timezone.now)
    description = models.TextField(null=True, blank=True)

class Advertisement(models.Model):
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='ads/')
    link = models.URLField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

class Artist(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Song(models.Model):
    title = models.CharField(max_length=100)
    mp3_file = models.FileField(upload_to='mp3s/')  # This uploads the file to media/mp3s
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, null=True, blank=True, default=None)
    uploaded_at = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return self.title

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

