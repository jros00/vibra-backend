from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    taste_profile_title = models.CharField(max_length=100, blank=True, null=True)
    taste_profile_color = models.CharField(max_length=7, blank=True, null=True)  # e.g., "#32CD32"
    profile_picture = models.ImageField(upload_to='profile_pics/', default='default.jpg')
    biography = models.TextField(max_length=500, blank=True)
    followers = models.ManyToManyField('self', symmetrical=False, related_name='following', blank=True)

    def __str__(self):
        return f'{self.user.username} Profile'

    def followers_count(self):
        return self.followers.count()

    def following_count(self):
        return self.following.count()
