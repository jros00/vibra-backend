# Mood-related views
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from home.models import VisualContent

class ChangeMoodView(APIView):
    def post(self, request):
        # Get the mood from the request data (POST data)
        mood = request.data.get('mood')
        
        # Store the mood in the session (or save it to the database if needed)
        request.session['mood'] = mood
        
        # Return a response confirming the mood change
        return Response({"message": f"Mood changed to {mood}"})