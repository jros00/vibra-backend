from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.request import Request

class LoginView(viewsets.ViewSet):
    """
    ViewSet to handle the login process and authenticate the user.
    """
    
    def retrieve(self, request: Request):
        username = 'user1'
        
        return self.create_user(username, request)
        
    def create(self, request: Request):
        username = request.data.get('username')
        
        return self.create_user(username, request)
    
    def create_user(self, username, request):
        password = 'password123'
        
        # Get or create the user
        user, created = User.objects.get_or_create(
            username=username,
            defaults={'password': password},
        )

        if created:
            # If the user is created, set the password (hashed)
            user.set_password(password)
            user.save()
            print(f"User '{username}' was created with the password '{password}'.")
        else:
            print(f"User '{username}' already exists.")

        # Authenticate the user
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)  # Log the user in
            return Response({"message": "User authenticated and logged in."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

            
    
    