from django.db import models
from django.contrib.auth.models import User


class MessageGroup(models.Model):
    group_name = models.CharField(max_length=50, blank=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_message_groups')
    members = models.ManyToManyField(User, related_name='joined_message_groups')
    timestamp = models.DateTimeField(auto_now_add=True)


class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    recipient = models.ForeignKey(MessageGroup, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.sender.username} to group {self.recipient.group_name}"

    class Meta:
        ordering = ['timestamp']
