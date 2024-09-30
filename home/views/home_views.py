# General home-related views

from django.shortcuts import render
from rest_framework import status, viewsets
from rest_framework.response import Response

class WelcomeView(viewsets.ViewSet):
    def create(self, request):
        name = request.user
        data = {
            "message": "Welcome to Vibra {name}!",
        }

        return Response(data, status=status.HTTP_200_OK)
    def list(self, request):
        # Prepare the data to return
        data = {
            "message": "Welcome to Vibra!",
        }

        return Response(data, status=status.HTTP_200_OK)