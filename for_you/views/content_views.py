# content views related to users
from rest_framework.request import Request
from rest_framework.response import Response
from core.models import Track
from core.serializers import TrackSerializer
from core.utils import cosine_distance
from rest_framework import status, viewsets
import numpy as np
import logging
import random
from django.shortcuts import get_object_or_404


logger = logging.getLogger(__name__)

class FetchTrackView(viewsets.ViewSet):
    def retrieve(self, request, pk=None):
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
        track_id = request.data.get('track_id')
        track = get_object_or_404(Track, track_id=track_id)
        serializer = TrackSerializer(track, partial=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class FetchRecommendedTracksView(FetchTrackView): 
    '''Fetch a list of recommended tracks based on the current track.'''
    def create(self, request: Request):
        track_id = request.data.get('track_id')
        curr_track = get_object_or_404(Track, track_id=track_id)
        response = self.main_function(curr_track, request)
        return response
        
    def list(self, request: Request):
        
        tracks = list(Track.objects.all())
        random_track = random.choice(tracks)
        response = self.main_function(random_track, request)
        return response

    def main_function(self, track, request: Request):
        '''Fetch recommended tracks based on the current track's audio features.'''
        track_results = TrackSerializer(track).data
        similar_tracks = self.fetch_similar_tracks(track_results)
        return Response(similar_tracks, status=status.HTTP_200_OK)
  
    
    def fetch_similar_tracks(self, curr_track_results):
        '''Fetch similar tracks based on cosine similarity of audio features.'''
        
        # Fetch all other tracks excluding the current one, along with their audio features
        all_tracks = Track.objects.exclude(track_id=curr_track_results["track_id"]).select_related('audiofeature')
        track_id = request.data.get("track_id")

        # If 'track_id' is not provided, return a 400 error response
        if not track_id:
            return Response({"error": "Missing track_id"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Call a helper method to process and return track data
        track_processor = FetchTrackView()
    
        similar_tracks = []

        # Ensure the current track has valid audio features
        curr_mfcc = curr_track_results['audio_features'].get('mfcc_mean', None)
        curr_tempo = curr_track_results['audio_features'].get('tempo', None)
        curr_chroma = curr_track_results['audio_features'].get('chroma_mean', None)
        if curr_mfcc is None or curr_tempo is None or curr_chroma is None:
            return []  # No valid audio features, return empty list

        for track in all_tracks:
            audio_feature = getattr(track, 'audiofeature', None)

            # Skip tracks without audio features
            if not audio_feature:
                continue

            # Calculate cosine distance between features
            try:
                distance = sum([
                    cosine_distance(np.array(curr_mfcc), np.array(audio_feature.mfcc_mean)),
                    cosine_distance(curr_tempo, audio_feature.tempo),
                    cosine_distance(np.array(curr_chroma), np.array(audio_feature.chroma_mean))
                ])
            except Exception as e:
                logger.error(f"Error calculating cosine distance for track {track.track_id}: {e}")
                continue

            # Attach the distance to the track object
            track.distance = distance

            similar_tracks.append(track)

        # Sort by similarity (lower distance = more similar)
        similar_tracks = sorted(similar_tracks, key=lambda x: x.distance)[:5]  # Top 5 similar tracks

        # Serialize the similar tracks using the TrackSerializer
        serialized_tracks = TrackSerializer(similar_tracks, many=True).data
        return serialized_tracks
