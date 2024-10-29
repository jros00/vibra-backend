from django.urls import path
from .views import ProfileView, EditBiographyView

urlpatterns = [
    path('<str:username>/', ProfileView.as_view(), name='profile-view'),  # View profile by username
    path('profile/edit/', EditBiographyView.as_view(), name='edit-biography'),    # Edit biography
]