# content views related to users
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from core.models import UserActivity, VisualContent, Song
from ml_tools_app.ml_utils import load_model  # Import the load_model function
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver


#@login_required
def user_viewed_articles(request):
    # Query the ContentView model for the current user's viewed articles
    content_views = ContentView.objects.filter(user=request.user).select_related('content').order_by('-timestamp')
    
    # Prepare a list of viewed articles with relevant data
    viewed_articles_data = [
        {
            'title': view.content.title,
            'id': view.content.id,
            'viewed_on': view.timestamp,
        }
        for view in content_views
    ]
    
    # Return the data as a JSON response
    return JsonResponse(viewed_articles_data, safe=False)

class PredictionView(APIView):
    def get(self, request):
        # Get the current mood from the session (default to 'neutral' if not set)
        current_mood = request.session.get('mood', 'neutral')
        
        # Filter content based on the mood (assuming the VisualContent model has a 'mood' field)
        #content = VisualContent.objects.filter(mood=current_mood)
        content = Song.objects
        # Return the mood-specific content
        return Response({
            "mood": current_mood,
            "content": list(content.values('title')),
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
