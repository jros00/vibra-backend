from django.urls import path
from .views import MessagePage, ChatListPage

urlpatterns = [
    path('chats/<int:group_id>/message/', MessagePage.as_view(), name='message_page'),
    path('messages/<int:recipient_id>/', MessagePage.as_view(), name='message_page'),
    path('chats/', ChatListPage.as_view(), name='chat_list')
]
