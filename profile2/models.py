from django.db import models

# Create your models here. Create SQL tables. Specific models for the profile app.
# Django has built-in functions to create users, but it lacks some features like profile picture etc, auth_user is the name of the table

from django.contrib.auth.models import User #It has some features already like the name, email password

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pics/', default='default.jpg')
    biography = models.TextField(max_length=500, blank=True)
    followers = models.ManyToManyField('self', symmetrical=False, related_name='following', blank=True)

    def __str__(self):
        return f'{self.user.username} Profile'

    def followers_count(self):
        return self.followers.count()

    def following_count(self):
        return self.following.count()