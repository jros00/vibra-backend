from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status, viewsets
from action.serializers import UserPreferenceSerializer


class RateView(viewsets.ViewSet):
    '''Handles likes and dislikes'''
    def create(self, request: Request):
        serializer = UserPreferenceSerializer(data=request.data, context={'request': request})#, partial=True) 
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 
