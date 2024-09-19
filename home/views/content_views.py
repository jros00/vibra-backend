# content views related to users
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from home.models import *
from common.ml_utils import load_model  # Import the load_model function

class PredictionView(APIView):
    def get(self, request):
        # Get the current mood from the session (default to 'neutral' if not set)
        current_mood = request.session.get('mood', 'neutral')
        
        # Filter content based on the mood (assuming the VisualContent model has a 'mood' field)
        content = VisualContent.objects.filter(mood=current_mood)
        
        # Return the mood-specific content
        return Response({
            "mood": current_mood,
            "content": list(content.values('title', 'image')),
        })

    def post(self, request):
        # Extract input features from the request
        features = request.data.get('features', [])
        
        # Format the features as a 2D array for model input
        model_input = [features]

        # Load the model and make a prediction
        # could import  Spotlight (Pytorch) that is spotify's own prediction model
        model = load_model()
        prediction = model.predict(model_input)

        # Map the prediction result to a class name (optional)
        class_names = ['Setosa', 'Versicolor', 'Virginica']
        predicted_class = class_names[prediction[0]]

        return Response({'predicted_class': predicted_class})
