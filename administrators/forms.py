# In your forms.py
from django import forms
from promotions.models import Question,Subcategory
from parler.forms import TranslatableModelForm

class QuestionForm(TranslatableModelForm):
    # These fields will automatically map to the translated fields in the model
    question_ar = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}), required=True)
    question_en = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}), required=True)

    class Meta:
        model = Question
        fields = ['question_ar', 'question_en']  # You only need these fields

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Manually save translations for Arabic and English
        if 'question_ar' in self.cleaned_data:
            instance.set_current_language('ar')
            instance.question = self.cleaned_data['question_ar']
        
        if 'question_en' in self.cleaned_data:
            instance.set_current_language('en')
            instance.question = self.cleaned_data['question_en']
        
        if commit:
            instance.save()
        
        return instance

class SubcategoryForm(TranslatableModelForm):
    subcategory_ar = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 1}), required=True)
    subcategory_en = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 1}), required=True)

    class Meta:
        model = Subcategory
        fields = ['subcategory_ar', 'subcategory_en'] 

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        if 'subcategory_ar' in self.cleaned_data:
            instance.set_current_language('ar')
            instance.subcategory = self.cleaned_data['subcategory_ar']
        
        if 'subcategory_en' in self.cleaned_data:
            instance.set_current_language('en')
            instance.subcategory = self.cleaned_data['subcategory_en']
        
        if commit:
            instance.save()
        
        return instance
