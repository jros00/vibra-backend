from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from random import randint, choice
from user_messages.models import MessageGroup
from profile2.models import Profile
import os
import pandas as pd
from user_messages.models import Message
from core.models import Track
from django.core.files import File




class Command(BaseCommand):
    help = 'Load some users and chats into the database'

    def handle(self, *args, **kwargs):
        usernames = ['Emilia', 'Johannes', 'Hugo', 'Oscar', 'Laura']
        
        group_attributes = {
            'house': 'The House Arrest Crew',
            'electronic': 'The Electrolytes',
            'hiphop': 'Vibe Tribe',
            'chillout': 'The Zen Dwellers',
        }
        
        track_messages = [
            'Check out this track!',
            'This track is great!',
            'Have you listened to this?',
            "Don't miss this out!",
        ]
        
        for username in usernames:
            user = User.objects.create_user(username=username, password='password123')
            profile = Profile.objects.get(user=user)
            profile_picture_path = os.path.join('media/profile_pictures', f'{user}.jpg')
            
            with open(profile_picture_path, 'rb') as image_file:
                profile.profile_picture.save(f'{username}.jpg', File(image_file), save=True)

        all_users = list(User.objects.all())
            
        for genre, group_name in group_attributes.items():
            creator = choice(all_users)
            group = MessageGroup.objects.create(group_name=group_name, creator=creator)
            group.members.add(*all_users)
            conversations_path = os.path.join('media/conversations', f'{genre}.csv')
            print('conversations_path', conversations_path)
            try:
                df = pd.read_csv(conversations_path, encoding='utf-8')
            except pd.errors.EmptyDataError:
                print(f"Warning: {conversations_path} is empty or not properly formatted.")
                continue
            all_tracks = Track.objects.all()
            tracks_within_genre = [track for track in all_tracks if genre in track.genre]
            
            for message in df['Message']:
                track_message = randint(0,5)
                if track_message == 0:
                    sender = choice(all_users)
                    content = choice(track_messages)
                    track = choice(tracks_within_genre)
                    tracks_within_genre.remove(track)
                    Message.objects.create(sender=sender, recipient=group, content=content, track=track)
                    
                sender = choice(all_users)
                content = message
                Message.objects.create(sender=sender, recipient=group, content=message)
        
        
        
            
        
        
        
            