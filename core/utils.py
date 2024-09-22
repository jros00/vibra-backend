# core/utils.py
import librosa
import numpy as np

def extract_audio_features_from_raw(y, sr):
    """
    Extract audio features (MFCC, tempo, and chroma) from the raw audio data.

    :param y: Audio time series.
    :param sr: Sample rate of the audio.
    :return: Tuple containing MFCC features (as a list), tempo, and chroma features.
    """
    try:
        # Extract MFCC features
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        # Extract tempo
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        # Extract chroma features
        chroma = librosa.feature.chroma_stft(y=y, sr=sr)

        # Take the mean of MFCC and chroma features over time
        mfcc_mean = mfccs.mean(axis=1).tolist()  # Convert NumPy array to list
        chroma_mean = chroma.mean(axis=1).tolist()  # Convert NumPy array to list
        
        return mfcc_mean, tempo, chroma_mean
    except Exception as e:
        print(f"Error extracting audio features: {e}")
        return None, None, None

def euclidean_distance(feature1, feature2):
    """
    Calculate the Euclidean distance between two feature arrays.
    """
    return np.linalg.norm(np.array(feature1) - np.array(feature2))