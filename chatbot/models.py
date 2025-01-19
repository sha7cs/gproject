from django.db import models
from users_app.models import UsersModel  # Import your custom user model

class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True)
    def __str__(self):
        return self.name

class Subcategory(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    description = models.TextField(null=True,blank=True)

    def __str__(self):
        return self.name

class Question(models.Model):
    text = models.TextField()
    subcategory = models.ForeignKey(Subcategory, on_delete=models.CASCADE, related_name='questions')

    def __str__(self):
        return self.text

