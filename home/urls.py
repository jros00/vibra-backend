from django.urls import path
from .views.home_views import HomeView

urlpatterns = [
    path('home/', HomeView.as_view(), name='home')
]