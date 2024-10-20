from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import Profile
from django.contrib.auth.models import User

# Create a profile when a user is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

# Save the profile when the user is saved
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()