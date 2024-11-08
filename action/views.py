from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status, viewsets
from action.serializers import UserPreferenceSerializer, MultipleListeningHistorySerializer, ListeningHistorySerializer, ShareSerializer
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from user_messages.serializers import MessageSerializer

class RateView(viewsets.ViewSet):
    '''Handles likes and dislikes'''
    def create(self, request: Request):
        serializer = UserPreferenceSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 


class ListeningHistoryView(viewsets.ViewSet):
    """
    ViewSet to handle the bulk creation of listening history records.
    """
    def create(self, request: Request):
        # Initialize the serializer with the request data
        serializer = MultipleListeningHistorySerializer(data=request.data, context={'request': request}, partial=True)

        if serializer.is_valid():
            # Use save() to create the listening history entries
            created_histories = serializer.save()

            # Return the serialized data for the created histories
            return Response(
                ListeningHistorySerializer(created_histories, many=True, context={'request': request}).data,
                status=status.HTTP_201_CREATED
            )

        # If validation fails, return the errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ShareView(viewsets.ViewSet):
    def create(self, request: Request):
        channel_layer = get_channel_layer()
        
        serializer = ShareSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            created_messages = serializer.save()
            
            # Loop over each group_id and send the message to its channel
            for created_message in created_messages:
                group_id = created_message.recipient.pk  
                async_to_sync(channel_layer.group_send)(
                    str(group_id),  
                    {
                        'type': 'chat_message',
                        'message': MessageSerializer(created_message).data # Serializes each object to the proper format for frontend
                    }
                )
            return Response(status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            

