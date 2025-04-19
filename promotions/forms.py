from django import forms
from promotions.models import Event

class EventForm(forms.ModelForm):
    name_en = forms.CharField(label="Event Name (English)", max_length=255)
    name_ar = forms.CharField(label="Event Name (Arabic)", max_length=255)
    description = forms.CharField(label="Description", widget=forms.Textarea, required=False)

    class Meta:
        model = Event
        fields = ['name_en', 'name_ar', 'description', 'date']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        event = super().save(commit=False)
        if self.user:
            event.user = self.user  
        if commit:
            event.save()
        return event
