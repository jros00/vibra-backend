from django.urls import path, include
from .views.advertisement_views import AdvertisementView
from .views.content_views import PredictionViewSet
from .views.mood_views import ChangeMoodView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'predict', PredictionViewSet, basename='predict')

urlpatterns = [
    #path('content/', PredictionView.as_view(), name='content'),
    path('advertisements/', AdvertisementView.as_view(), name='home'),
    path('change-mood/', ChangeMoodView.as_view(), name='mood'),
    #path('predict/<str:track_id>/', PredictionView.as_view(), name='predict_tracks'), 
    path('', include(router.urls)),
]