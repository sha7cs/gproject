from django.db import models
from users_app.models import UsersModel  # Import your custom user model

class ChatSession(models.Model):
    user = models.ForeignKey(UsersModel, on_delete=models.CASCADE, related_name="chat_sessions")
    thread_id = models.CharField(max_length=100, unique=True)  # Unique thread_id for each user
    messages = models.JSONField(default=list)  # Store conversation history as JSON
    created_at = models.DateTimeField(auto_now_add=True)  # Track session creation time

    def __str__(self):
        return f"ChatSession for {self.user.email} (Thread: {self.thread_id})"


