from django.contrib import admin
from .models import Subcategory, Category,Question
from parler.admin import TranslatableAdmin
from .models import Event
# Register your models here.


# admin.site.register(Subcategory,TranslatableAdmin)
# admin.site.register(Category,TranslatableAdmin)
# admin.site.register(Question,TranslatableAdmin)



@admin.register(Event)
class EventAdmin(TranslatableAdmin):
    list_display = ('name', 'date', 'user')
    search_fields = ('translations__name',)
    list_filter = ('date', 'user')

@admin.register(Category)
class CategoryAdmin(TranslatableAdmin):
    list_display = ('__str__',)

@admin.register(Subcategory)
class SubcategoryAdmin(TranslatableAdmin):
    list_display = ('__str__', 'category')

@admin.register(Question)
class QuestionAdmin(TranslatableAdmin):
    list_display = ('__str__', 'subcategory')
