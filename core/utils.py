# core/utils.py
import librosa
import numpy as np
import joblib
import os
from django.conf import settings

# Path to the saved model file
MODEL_PATH = os.path.join(settings.BASE_DIR, 'models', 'my_model.pkl')

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

def cosine_distance(feature1, feature2):
    """
    Calculate the Cosine distance between two feature arrays.
    Cosine distance = 1 - Cosine similarity
    """
    # Convert inputs to numpy arrays
    feature1 = np.array(feature1)
    feature2 = np.array(feature2)
    
    # Compute the dot product of the two feature vectors
    dot_product = np.dot(feature1, feature2)
    
    # Compute the magnitudes (norms) of the feature vectors
    norm_feature1 = np.linalg.norm(feature1)
    norm_feature2 = np.linalg.norm(feature2)
    
    # Calculating cosine similarity
    cosine_similarity = dot_product / (norm_feature1 * norm_feature2)
    
    # Calculating cosine distance
    cosine_distance = 1 - cosine_similarity
    return cosine_distance


def load_model():
    """
    Load the machine learning model from the file system.
    This function loads the model once and reuses it to make predictions.
    """
    # Load the pre-trained model using joblib
    model = joblib.load(MODEL_PATH)
    return model