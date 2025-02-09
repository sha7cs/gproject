from django.db import models
from users_app.models import UsersModel  # Import your custom user model
from django.utils.translation import gettext_lazy as _
from parler.models import TranslatableModel,TranslatedFields # this for tranlating models i dont think we need it 
from django.db import models

class Category(TranslatableModel):
    translations = TranslatedFields(
        category=models.CharField(_('category'), max_length=255),
        description=models.TextField(_('description'), null=True),
    )

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
        ordering = ['id']  # Adjust ordering as needed

    def __str__(self):
        return self.category


class Subcategory(TranslatableModel):
    translations = TranslatedFields(
        subcategory=models.CharField(_('subcategory'), max_length=255),
        description=models.TextField(_('description'), null=True, blank=True)
    )
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')

    class Meta:
        verbose_name = _('Subcategory')
        verbose_name_plural = _('Subcategories')
        ordering = ['id']

    def __str__(self):
        return self.subcategory


class Question(TranslatableModel):
    translations = TranslatedFields(
        question=models.TextField(_('question')),
    )
    subcategory = models.ForeignKey(Subcategory, on_delete=models.CASCADE, related_name='questions')

    class Meta:
        verbose_name = _('Question')
        verbose_name_plural = _('Questions')
        ordering = ['id']

    def __str__(self):
        return self.question


class DailyAdvice(TranslatableModel):
    translations = TranslatedFields(
        title=models.CharField(_('title'), max_length=255),
        advice=models.TextField(_('advice')),
    )
    
    class Meta:
        verbose_name = _('Daily Advice')
        verbose_name_plural = _('Daily Advices')
        ordering = ['id']

    def __str__(self):
        return self.title
