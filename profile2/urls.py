# connect urls with views
from django.urls import path
from .views import profile_view, edit_biography_view

urlpatterns = [
    path('<str:username>/', profile_view, name='profile'),
    path('edit/', edit_biography_view, name='edit_biography'),
]