from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views.advertisement_views import AdvertisementView
from .views.content_views import FetchRecommendedTracksView, FetchTrackView, FirstTrackView
from .views.mood_views import ChangeMoodView

router = DefaultRouter()
router.register(r'first_track', FirstTrackView, basename='first_track')
router.register(r'recommended', FetchRecommendedTracksView, basename='recommended')
router.register(r'track', FetchTrackView, basename='track')

urlpatterns = [
    path('', include(router.urls)),
]