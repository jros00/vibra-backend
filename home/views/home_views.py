# General home-related views

from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response

class HomeView(APIView):
    def get(self, request):
        # Prepare the data to return
        data = {
            "message": "Welcome to Vibra App!",
        }

        return Response(data)