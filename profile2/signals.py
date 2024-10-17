from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import Profile
from django.contrib.auth.models import User

'''
Put signals in a separate file for them to be able to register before the profile page is accessed. 
The signals should already be registered when the script  load_chats is executed. 
Otherwise new profile pages will never be generated. see .apps.py
'''
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()