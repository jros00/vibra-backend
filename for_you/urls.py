from django.urls import path
from .views.advertisement_views import AdvertisementView
from .views.content_views import PredictionView
from .views.mood_views import ChangeMoodView

urlpatterns = [
    path('content/', PredictionView.as_view(), name='content'),
    path('advertisements/', AdvertisementView.as_view(), name='home'),
    path('change-mood/', ChangeMoodView.as_view(), name='mood'),
]