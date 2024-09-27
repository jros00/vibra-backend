from django.urls import include, path
from rest_framework.routers import DefaultRouter

from action.views import RateView

router = DefaultRouter()

router.register(r'rate', RateView, basename='rate')

urlpatterns = [
    path('', include(router.urls)),
]