import json
from django.shortcuts import redirect, render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import pusher
import json
from .models import ChatRoom, Message
from django.conf import settings
from chapchap.models import CustomUser

pusher_client = pusher.Pusher(
    app_id=settings.PUSHER_APP_ID,
    key=settings.PUSHER_KEY,
    secret=settings.PUSHER_SECRET,
    cluster=settings.PUSHER_CLUSTER,
    ssl=True
)

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import ChatRoom, Message
from chapchap.models import Product



from django.shortcuts import get_object_or_404, redirect
from .models import ChatRoom, Message
from chapchap.models import Product, CustomUser
@login_required
def start_or_continue_chat(request, product_id):
    """Ensure a new chat is created for each different product, even if users have chatted before."""
    product = get_object_or_404(Product, id=product_id)
    product_owner = product.user
    buyer = request.user  # The user clicking the chat button

    # Ensure the buyer isn't chatting with themselves
    if buyer == product_owner:
        return redirect('product_detail', product_id=product.id)

    # Check if a chat room already exists **for this specific product**
    chat_room = ChatRoom.objects.filter(users=buyer).filter(users=product_owner).filter(product=product).first()

    # If no chat room exists, create one
    if not chat_room:
        chat_room = ChatRoom.objects.create(product=product)  # Ensure product is linked
        chat_room.users.add(buyer, product_owner)
        chat_room.save()

    return redirect('chat:chat_room_detail', chat_room_id=chat_room.id)


@login_required
def user_chats(request):
    """Show all chat rooms the user is part of."""
    chat_rooms = ChatRoom.objects.filter(users=request.user)
    return render(request, 'user_chats.html', {'chat_rooms': chat_rooms})

@login_required
def chat_room_detail(request, chat_room_id):
    chat_room = get_object_or_404(ChatRoom, id=chat_room_id)
    
    # Get the product associated with the chat room
    product = chat_room.product  
    product_owner = product.user  # Get the user who created the product

    # Check if the user is part of the chat room
    if request.user not in chat_room.users.all():
        return redirect('chat:user_chats')  # Redirect to user's chat list

    # Fetch all messages for the chat room
    messages = chat_room.messages.all()

    # ✅ Mark all unread messages as read when the user opens the chat
    chat_room.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)

    # ✅ Trigger Pusher to update the unread message count in the chat list
    new_message_count = chat_room.messages.filter(is_read=False).count()
    pusher_client.trigger('chat_list_channel', 'update_message_count', {
        'chat_room_id': chat_room.id,
        'new_message_count': new_message_count
    })

    return render(request, 'chat.html', {
        'product': product,
        'messages': messages,
        'chat_room': chat_room,
    })


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import ChatRoom, Message  # Import your models
from chapchap.models import CustomUser  # Import CustomUser model from the correct app


from django.http import JsonResponse
import asyncio

async def async_view(request):
    await asyncio.sleep(2)  # Simulate async task
    return JsonResponse({"message": "Async response!"})


from django.utils.timezone import make_aware
from datetime import datetime

@csrf_exempt
def send_message(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            chat_room_id = data.get("chat_room_id")
            sender_id = data.get("sender_id")
            message_content = data.get("message")

            if not message_content.strip():
                return JsonResponse({"status": "error", "message": "Message cannot be empty"})

            chat_room = get_object_or_404(ChatRoom, id=chat_room_id)
            sender = get_object_or_404(CustomUser, id=sender_id)

            # Create the message
            message = Message.objects.create(chat_room=chat_room, sender=sender, content=message_content)

            # Convert timestamp to UTC explicitly
            utc_timestamp = message.timestamp.astimezone().strftime("%Y-%m-%dT%H:%M:%S.%fZ")

            # Send the new message via Pusher
            pusher_client.trigger(f'chat_{chat_room_id}', 'new_message', {
                'message': message.content,
                'sender_id': sender.id,
                'sender_name': sender.username,
                'chat_room_id': chat_room.id,
                'timestamp': utc_timestamp  # Now timestamp is in ISO 8601 UTC format
            })

            return JsonResponse({
                "status": "success",
                "message": message.content,
                "sender_id": sender.id
            })

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})
