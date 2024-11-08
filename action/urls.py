from django.urls import include, path
from rest_framework.routers import DefaultRouter
from action.views import RateView, ListeningHistoryView, ShareView

router = DefaultRouter()

router.register(r'rate', RateView, basename='rate')
router.register(r'listening_history', ListeningHistoryView, basename='listening_history')
router.register(r'share', ShareView, basename='share')

urlpatterns = [
    path('', include(router.urls)),
]