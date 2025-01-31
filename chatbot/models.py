from django.db import models
from users_app.models import UsersModel  # Import your custom user model
from django.utils.translation import gettext_lazy as _
from parler.models import TranslatableModel,TranslatedFields # this for tranlating models i dont think we need it 

class Category(TranslatableModel):
    translations = TranslatedFields (
        category = models.CharField(_('category'),max_length=255),
        description = models.TextField(_('description'),null=True),
    )
    def __str__(self):
        return self.category

class Subcategory(TranslatableModel):
    translations = TranslatedFields (
        subcategory = models.CharField(_('subcategory'),max_length=255),
        description = models.TextField(_('description'),null=True,blank=True)
    )
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    def __str__(self):
        return self.subcategory

class Question(TranslatableModel):
    translations = TranslatedFields (
        question = models.TextField(_('question')),
        question_ar = models.TextField(),
    )
    subcategory = models.ForeignKey(Subcategory, on_delete=models.CASCADE, related_name='questions')
    #)
    def __str__(self):
        return self.question
