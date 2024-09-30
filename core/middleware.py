from django.shortcuts import redirect
from django.conf import settings
from django.urls import reverse
from django.middleware.csrf import get_token


class LoginRequiredMiddleware:
    """
    Middleware to ensure that users are authenticated for every page except login, signup, and other public pages.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get or create the CSRF token
        csrf_token = get_token(request)
        
        # Set it in the request headers
        request.META['HTTP_X_CSRFTOKEN'] = csrf_token
        
        # List of exempt URLs that don't require login
        exempt_urls = [reverse('login_view')]

        if not request.user.is_authenticated and request.path not in exempt_urls:
            print('user:', request.user)
            return redirect(reverse('login_view'))  # Redirect to login view

        # Continue processing the request
        response = self.get_response(request)
        return response
