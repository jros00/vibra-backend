from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from random import randint, sample, choice
from user_messages.models import MessageGroup




class Command(BaseCommand):
    help = 'Load some users and chats into the database'

    group_names = [
    "Harmony Seekers",
    "Melody Mavens",
    "Rhythm Riders",
    "Tune Tribe",
    "Chords Collective",
    "Beat Enthusiasts",
    "Acoustic Admirers",
    "Symphony Society",
    "Groove Gatherers",
    "Tempo Troopers",
    "Soundwave Syndicate",
    "Crescendo Crew",
    "Bassline Brotherhood",
    "Treble Tribe",
    "Melodic Minds",
    "Harmonic Heroes",
    "Vibe Virtuosos",
    "Note Navigators",
    "Pitch Pioneers",
    "Sonata Squad",
    "Echo Enthusiasts",
    "Fret Fanatics",
    "Octave Oracles",
    "Sound Sculptors",
    "Syncopation Squad",
    "Key Signature Keepers",
    "Chord Charmers",
    "Tempo Travelers",
    "Decibel Dreamers",
    "Resonance Revelers"
    ]

    def handle(self, *args, **kwargs):
        users = ['Emilia', 'Johannes', 'Hugo', 'Oscar', 'Laura']
        
        for user in users:
            User.objects.create_user(username=user, password='password123')
    
        all_users = list(User.objects.all())
            
        for _ in range(30): # Creating 30 random chats
            num_participants = randint(2,5)
            members = sample(all_users, num_participants)
            group_name = choice(self.group_names)
            self.group_names.remove(group_name)
            group = MessageGroup.objects.create(group_name=group_name, creator=members[0])
            group.members.add(*members)
        
        
        
            
        
        
        
            