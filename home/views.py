from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response

# Create your views here.

# NOTE: Test view
class WelcomeView(APIView):
    def get(self, request):
        data = {
            "message": "Welcome to Vibra App!"
        }
        return Response(data)