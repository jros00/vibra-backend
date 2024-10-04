from django.urls import include, path
from rest_framework.routers import DefaultRouter
from action.views import RateView, ListeningHistoryView

router = DefaultRouter()

router.register(r'rate', RateView, basename='rate')
router.register(r'listening_history', ListeningHistoryView, basename='listening_history')

urlpatterns = [
    path('', include(router.urls)),
]