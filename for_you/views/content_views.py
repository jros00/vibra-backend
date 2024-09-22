# content views related to users
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from core.models import UserActivity, VisualContent, Song, Track, AudioFeature, ContentView

from ml_tools_app.ml_utils import load_model  # Import the load_model function
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
import numpy as np
from rest_framework import status
from rest_framework.decorators import action
from rest_framework import viewsets
from core.utils import euclidean_distance

class PredictionViewSet(viewsets.ViewSet):

    @action(detail=True, methods=['get'])
    def predict(self, request, pk=None):
        try:
            # Fetch the track by ID
            current_track = Track.objects.get(track_id=pk)
        except Track.DoesNotExist:
            return Response({"error": "Track not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            # Fetch the audio features for the track
            current_audio_feature = AudioFeature.objects.get(track=current_track)
        except AudioFeature.DoesNotExist:
            return Response({"error": "Audio features not found"}, status=status.HTTP_404_NOT_FOUND)

        # Fetch all other tracks to compare against the current track
        all_tracks = Track.objects.exclude(track_id=pk)
        similar_tracks = []

        for track in all_tracks:
            try:
                # Get the audio features of each track
                audio_feature = AudioFeature.objects.get(track=track)
                # Calculate the Euclidean distance between MFCCs
                distance = euclidean_distance(current_audio_feature.mfcc_mean, audio_feature.mfcc_mean)
                similar_tracks.append((track, distance))
            except AudioFeature.DoesNotExist:
                # Skip if the track doesn't have audio features
                continue

        # Sort by similarity (lower distance = more similar)
        similar_tracks = sorted(similar_tracks, key=lambda x: x[1])[:5]  # Top 5 similar tracks

        # Prepare the response with similar tracks, using Jamendo URLs instead of local URLs
        return Response({
            "track_title": current_track.track_title,
            "audio_url": current_track.audio_url,  # Jamendo URL for the current track
            "similar_tracks": [
                {
                    "track_id": t[0].track_id,
                    "track_title": t[0].track_title,
                    "artist_name": t[0].artist_name,
                    "audio_url": t[0].audio_url,  # Jamendo URL for similar tracks
                    "distance": t[1]
                } for t in similar_tracks
            ]
        }, status=status.HTTP_200_OK)
