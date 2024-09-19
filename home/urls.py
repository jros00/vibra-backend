from django.urls import path
from .views.advertisement_views import AdvertisementView
from .views.home_views import HomeView
from .views.mood_views import ChangeMoodView
from .views.content_views import PredictionView

urlpatterns = [
    path('home/', HomeView.as_view(), name='home'),
    path('content/', PredictionView.as_view(), name='content'),
    path('advertisements/', AdvertisementView.as_view(), name='home'),
    path('change-mood/', ChangeMoodView.as_view(), name='mood'),
]