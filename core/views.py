from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
from django.middleware.csrf import get_token


class UserListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        users = User.objects.all().values('id', 'username')  # Select only needed fields
        return Response(users)


def get_csrf_token(request):
    # Ensure this view only allows GET requests
    if request.method == "GET":
        csrf_token = get_token(request)
        return JsonResponse({'csrfToken': csrf_token})
    else:
        return JsonResponse({"error": "Method not allowed"}, status=405)
