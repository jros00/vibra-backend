import numpy as np
from django.shortcuts import render
from .models import Track, AudioFeature

def euclidean_distance(feature1, feature2):
    return np.linalg.norm(np.array(feature1) - np.array(feature2))

def recommend_tracks_by_audio(request, track_id):
    current_track = Track.objects.get(track_id=track_id)
    current_audio_feature = AudioFeature.objects.get(track=current_track)

    all_tracks = Track.objects.exclude(track_id=track_id)
    similar_tracks = []

    for track in all_tracks:
        try:
            audio_feature = AudioFeature.objects.get(track=track)
            distance = euclidean_distance(current_audio_feature.mfcc_mean, audio_feature.mfcc_mean)
            similar_tracks.append((track, distance))
        except AudioFeature.DoesNotExist:
            continue

    # Sort by similarity (lower distance means more similar)
    similar_tracks = sorted(similar_tracks, key=lambda x: x[1])[:5]

    return render(request, 'core/recommendations.html', {
        'current_track': current_track,
        'similar_tracks': [t[0] for t in similar_tracks],
    })