from django.urls import path
from .views import MessagePage

urlpatterns = [
    path('messages/<int:recipient_id>/', MessagePage.as_view(), name='message_page'),
]
