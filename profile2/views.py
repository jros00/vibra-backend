from django.shortcuts import render, get_object_or_404
from .models import Profile
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from .serializers import ProfileSerializer
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

class ProfileView(APIView):  # Use APIView for better error handling
    def get(self, request: Request, username=None):  # Use username instead of pk
        print(f"Fetching profile for {username}")  # Add this to check
        try:
            # Fetch profile by username
            profile = Profile.objects.get(user__username=username)
        except Profile.DoesNotExist:
            return Response('Profile does not exist', status=status.HTTP_404_NOT_FOUND)

        serializer = ProfileSerializer(profile, context={'request': request})  # Serialize the profile data
        return Response(serializer.data, status=status.HTTP_200_OK)

# Handling the biography edit
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class EditBiographyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        print("POST request received")
        bio = request.data.get('biography')
        if not bio:
            return Response({"error": "Biography cannot be empty"}, status=status.HTTP_400_BAD_REQUEST)

        # Update the user's biography
        request.user.profile.biography = bio
        request.user.profile.save()
        return Response({"message": "Biography updated successfully"}, status=status.HTTP_200_OK)

