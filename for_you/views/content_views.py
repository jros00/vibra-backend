# content views related to users
from rest_framework.request import Request
from rest_framework.response import Response
from core.models import Track
from core.serializers import TrackSerializer, UserPreferenceSerializer, ListeningHistorySerializer
from core.utils import cosine_distance
from rest_framework import status, viewsets
import numpy as np
import logging
#from concurrent.futures import ThreadPoolExecutor, as_completed
import random
from django.forms.models import model_to_dict


logger = logging.getLogger(__name__)

class FetchTrackView(viewsets.ViewSet):
    '''Fetch a specific track by its track_id.'''
    
    def get_track_or_404(self, track_id):
        try:
            return Track.objects.get(track_id=track_id)
        except Track.DoesNotExist:
            return None

    def create(self, request: Request):
        track_id = request.data.get('track_id')
        track = self.get_track_or_404(track_id)
        if not track:
            return Response({"error": "Track not found"}, status=status.HTTP_404_NOT_FOUND)
        track_dict = model_to_dict(track)
        serializer = TrackSerializer(data=track_dict, instance=track)
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FetchRecommendedTracksView(FetchTrackView): 
    '''Still some bugs with registation of listening history'''
    def create(self, request: Request):
        track_id = request.data.get('track_id')
        curr_track = self.get_track_or_404(track_id)
        response = self.main_function(curr_track, request)
        return response
        
    def list(self, request: Request):
        '''Fetch recommended tracks based on the current track's audio features.'''
        tracks = list(Track.objects.all())
        random_track = random.choice(tracks)
        print(random_track)
        response = self.main_function(random_track, request)
        return response

    def main_function(self, track, request: Request):
        # Serialize the current track's data
        data = request.data
        track_results = TrackSerializer(track).data
        print(track_results)
        # Fetch the similar tracks based on current track's features
        similar_tracks = self.fetch_similar_tracks(track_results)
        # Perform the create requests for ListeningHistory (if needed)
        # Pass the track instance to the serializer
        serializer = ListeningHistorySerializer(data=data, context={'request': request, 'track_results': track_results}, partial = True)
        
        if serializer.is_valid():
            try:
                serializer.save()  # This will trigger the logic in `ListeningHistorySerializer`
                print('history created')
                print('log created')
                return Response(similar_tracks, status=status.HTTP_200_OK)
            except:
                # If only logging
                print('log created')
                return Response(similar_tracks, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        
    
    def fetch_similar_tracks(self, curr_track_results):
        '''Fetch similar tracks based on cosine similarity of audio features.'''
        
        # Fetch all other tracks excluding the current one, along with their audio features
        all_tracks = Track.objects.exclude(track_id=curr_track_results["track_id"]).select_related('audiofeature')

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


class Preferences(viewsets.ViewSet):
    '''Handles likes and dislikes'''
    def create(self, request: Request):
        if 'activity_type' in request.data:  # Liking or disliking
            preference_serializer = UserPreferenceSerializer(data=request.data)
            if preference_serializer.is_valid():
                preference_serializer.save()
                return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)  
