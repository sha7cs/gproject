from django.db import models

# Create your models here.

class UsersModel(models.Model):
    name = models.CharField(max_length=255)  # User's full name
    email = models.EmailField(unique=True)  # Ensures email is unique
    password = models.CharField(max_length=255)  # Store hashed password (use Django's auth system)
    thread_id = models.CharField(max_length=100, unique=True)  # Stores OpenAI thread ID for conversation

    created_at = models.DateTimeField(auto_now_add=True)  # Automatically set when a user is created
    updated_at = models.DateTimeField(auto_now=True)  # Auto-updates when modified

    def __str__(self):
        return self.name  # Displays name in Django Admin

