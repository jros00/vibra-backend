from django.urls import path
from .views import MessagePage, ChatListPage

urlpatterns = [
    path('<int:group_id>/messages/', MessagePage.as_view(), name='message_page'),
    path('messages/<int:recipient_id>/', MessagePage.as_view(), name='message_page'),
    path('', ChatListPage.as_view(), name='conversations')
]
