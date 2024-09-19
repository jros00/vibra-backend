from django.db import models

class User(models.Model):
    name = models.CharField(max_length=50)
    
    def __str__(self):
        return self.name

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
    mp3_file = models.FileField(upload_to='audio_files/')
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

class VisualContent(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='visual_content/')
    mood = models.CharField(max_length=50)  # Optional if content depends on mood
    song = models.ForeignKey(Song, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

