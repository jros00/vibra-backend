# content views related to users
import numpy as np
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.shortcuts import render
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import AudioFeature, Track, UserActivity
from core.utils import load_model  # Import the load_model function
from core.utils import euclidean_distance


class FetchTrackView(viewsets.ViewSet):

    # NOTE: create method: This is the correct method for POST in Django REST Framework.
    #  When a POST request is made to this view, the create method will be called.

    def create(self, request: Request):
        # Read 'track_id' from the POST request body
        track_id = request.data.get("track_id")

        # If 'track_id' is not provided, return a 400 error response
        if not track_id:
            return Response({"error": "Missing track_id"}, status=status.HTTP_400_BAD_REQUEST)

        # Call a helper method to process and return track data
        results = self.process_track(track_id)

        # Check if there's an error and handle it
        if 'error' in results:
            return Response(results, status=results.get('status', status.HTTP_400_BAD_REQUEST))

        # Send a success response (200 OK) with the data
        return Response(results, status=status.HTTP_200_OK)

    def process_track(self, track_id):
        try:
            track = Track.objects.get(track_id=track_id)
        except Track.DoesNotExist:
            return {"error": "Track not found", "status": status.HTTP_404_NOT_FOUND}

        try:
            audio_feature = AudioFeature.objects.get(track=track)
        except AudioFeature.DoesNotExist:
            return {"error": "Audio features not found", "status": status.HTTP_404_NOT_FOUND}

        # Return a dictionary of data that will be used in the Response object
        return {
            "track_id": track.track_id,
            "title": track.track_title,
            "audio_url": track.audio_url,
            "album_image": track.album_image,
            "album_name": track.album_name,
            "audio_features": {
                "chroma_mean": audio_feature.chroma_mean,
                "tempo": audio_feature.tempo,
                "mfcc_mean": audio_feature.mfcc_mean
            }
        }
 

class FetchRecommendedTracksView(viewsets.ViewSet):

    # NOTE: To be made much more complex later, for now just based on previously listened song

    def create(self, request: Request):
        # Read 'track_id' from the POST request body
        track_id = request.data.get("track_id")

        # If 'track_id' is not provided, return a 400 error response
        if not track_id:
            return Response({"error": "Missing track_id"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Call a helper method to process and return track data
        track_processor = FetchTrackView()
        curr_track_results = track_processor.process_track(track_id)
        if 'error' in curr_track_results:
            return Response(curr_track_results, status=curr_track_results.get('status', status.HTTP_400_BAD_REQUEST))
        
        results = self.fetch_similar_tracks(curr_track_results)
        return Response(results, status=status.HTTP_200_OK)


    def fetch_similar_tracks(self, curr_track_results):
        
        # Fetch all other tracks to compare against the current track
        all_tracks = Track.objects.exclude(track_id=curr_track_results["track_id"])
        similar_tracks = []

        for track in all_tracks:
            try:
                # Get the audio features of each track
                audio_feature = AudioFeature.objects.get(track=track)
                # Calculate the Euclidean distance between MFCCs
                distance = euclidean_distance(curr_track_results['audio_features']['mfcc_mean'], audio_feature.mfcc_mean)
                similar_tracks.append((track, distance))
            except AudioFeature.DoesNotExist:
                # Skip if the track doesn't have audio features
                continue

        # Sort by similarity (lower distance = more similar)
        similar_tracks = sorted(similar_tracks, key=lambda x: x[1])[:5]  # Top 5 similar tracks

        result = []
        for track_data in similar_tracks:
            track: Track = track_data[0]
            distance = track_data[1]
            track_results =  {
                    "track_id": track.track_id,
                    "track_title": track.track_title,
                    "artist_name": track.artist_name,
                    "audio_url": track.audio_url,  # Jamendo URL for similar tracks
                    "album_image": track.album_image,  # Return album image (track image) for similar tracks
                    "distance": distance
                }
            result.append(track_results)
        
        return result
    

class FirstTrackView(viewsets.ViewSet):

    # NOTE: Placeholder method to just recieve a track to start with
    # The list method is meant for handling GET requests to retrieve a collection or a default resource, 
    # which doesn't require a pk in the URL. 

    def list(self, request: Request):
        try:
            track = Track.objects.get(id=1)
        except Track.DoesNotExist:
            return {"error": "Track not found", "status": status.HTTP_404_NOT_FOUND}
        
        # Call a helper method to process and return track data
        track_processor = FetchTrackView()
        track_results = track_processor.process_track(track.track_id)
        if 'error' in track_results:
            return Response(track_results, status=track_results.get('status', status.HTTP_400_BAD_REQUEST))

        return Response(track_results, status=status.HTTP_200_OK)


        


