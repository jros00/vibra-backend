from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from home.models import Advertisement

class AdvertisementView(APIView):
    def get(self, request):
        ad = Advertisement.objects.first()  # or any logic for fetching an ad
        return Response({
            "ad": ad
        })