from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views.home_views import WelcomeView

router = DefaultRouter()
router.register(r'welcome', WelcomeView, basename='welcome')

urlpatterns = [
    path('', include(router.urls)),
]