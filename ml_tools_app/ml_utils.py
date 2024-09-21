import joblib
import os
from django.conf import settings

# Path to the saved model file
MODEL_PATH = os.path.join(settings.BASE_DIR, 'models', 'my_model.pkl')

def load_model():
    """
    Load the machine learning model from the file system.
    This function loads the model once and reuses it to make predictions.
    """
    # Load the pre-trained model using joblib
    model = joblib.load(MODEL_PATH)
    return model