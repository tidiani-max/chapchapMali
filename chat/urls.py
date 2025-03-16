from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('chats/', views.user_chats, name='user_chats'),
    path('chat/<int:chat_room_id>/', views.chat_room_detail, name='chat_room_detail'),
    path('start-chat/<int:product_id>/', views.start_or_continue_chat, name='start_or_continue_chat'),
    path('send_message/', views.send_message, name='send_message'),
]