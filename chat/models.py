from django.db import models
from django.conf import settings
from chapchap.models import Product

class ChatRoom(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  # Many chat rooms for one product
    users = models.ManyToManyField(settings.AUTH_USER_MODEL)

    def __str__(self):
        return f"Chat Room for {self.product.name} - {', '.join(user.username for user in self.users.all())}"

class Message(models.Model):
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False) 

    def __str__(self):
        return f"{self.sender.username}: {self.content[:20]}"
