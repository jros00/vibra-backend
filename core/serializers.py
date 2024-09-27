from rest_framework import serializers
from core.models import Track, AudioFeature


class AudioFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = AudioFeature
        fields = ['chroma_mean', 'tempo', 'mfcc_mean']


class TrackSerializer(serializers.ModelSerializer):
    '''Returns the full data of the Track, including its audio features'''
    # Reference the related AudioFeature object using the reverse relationship
    audio_features = AudioFeatureSerializer(read_only=True, source='audiofeature')

    class Meta:
        model = Track
        fields = ['track_id', 'track_title', 'artist_name', 'audio_url', 'audio_features']
        read_only_fields = ['track_id']