from django.urls import path, include
from .views.advertisement_views import AdvertisementView
from .views.content_views import PredictionViewSet
from .views.mood_views import ChangeMoodView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'for_you', PredictionViewSet, basename='for_you')

urlpatterns = [
    path('api/', include(router.urls)),
    path('advertisements/', AdvertisementView.as_view(), name='home'),
    path('change-mood/', ChangeMoodView.as_view(), name='mood'),
    path('', include(router.urls)),
]