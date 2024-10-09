from django.db import models
from django.contrib.auth.models import User
from core.models import Track
from django.core.exceptions import ValidationError


class MessageGroup(models.Model):
    group_name = models.CharField(max_length=50, blank=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_message_groups')
    members = models.ManyToManyField(User, related_name='joined_message_groups')
    timestamp = models.DateTimeField(auto_now_add=True)


class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    recipient = models.ForeignKey(MessageGroup, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField(blank=True, null=True)
    track = models.ForeignKey(Track, blank=True, null=True, on_delete=models.SET_NULL)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    def clean(self):
        # Ensure at least one of the two fields is filled
        if not self.content and not self.track:
            raise ValidationError('At least one of "content" or "track" must be provided.')

    def save(self, *args, **kwargs):
        # Call the clean method before saving
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Message from {self.sender.username} to group {self.recipient.group_name}"

    class Meta:
        ordering = ['timestamp']
