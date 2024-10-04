from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Notification
from django.contrib.auth.models import User
from notifications.utils import create_notification

class NotificationView(APIView):
    def get(self, request):
        notifications = Notification.objects.filter(user=request.user, is_read=False)
        data = [{'message': n.message, 'created_at': n.created_at} for n in notifications]
        return Response(data)

    def post(self, request):
        user = request.user
        message = request.data.get('message', '')
        if message:
            create_notification(user, message)
            return Response({"status": "Notification sent!"})
        return Response({"error": "Message cannot be empty"}, status=400)
