from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import User
from django.middleware.csrf import get_token

class AssignDummyUserMiddleware(MiddlewareMixin):

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        """
        Assign a dummy user and handle CSRF token for requests.
        """

        # Assign a dummy user for the request
        user, created = User.objects.get_or_create(
            username='user1',
            defaults={
                'email': 'user1@example.com'
            }
        )

        # Set password (if the user was just created)
        if created:
            user.set_password('12345')  # You should use a more secure password
            user.save()
            print("User created.")
        else:
            print("User already exists.")

        # Assign the user to the request
        request.user = user

        # Retrieve or set the CSRF token
        csrf_token = get_token(request)
        request.META['HTTP_X_CSRFTOKEN'] = csrf_token

        # Call the next middleware or view
        response = self.get_response(request)

        return response
