from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile,City,Area


#مثل ماتلاحظون هذي فورم جديد انهرت من الاصليه حقت جانقو ليه سوينا كذا؟ عشان نقدر نحكم بالاتربيوت الي نبيهم زي مثلا هنا زدت الايميل! 
class CreateUser(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)  # Save user instance but don't commit yet
        user.email = self.cleaned_data['email']  # Save email field
        if commit:
            user.save()  # Save to database
        return user
    
#هذي فورم حقت الستينقز والتعديلات المفروض ترتبط بالمودل (الي ماسويناه للحين) 
class UserProfileForm(forms.ModelForm):
    
    area = forms.ModelChoiceField(queryset=Area.objects.all(), empty_label="اختر", widget=forms.Select(attrs={'id': 'inputState5' ,'class':"form-control"}))
    city = forms.ModelChoiceField(queryset=City.objects.all(), empty_label="اختر", widget=forms.Select(attrs={'id': 'inputCity', 'class':"form-control"}))
 
    cafe_name = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={'class': 'form-control','placeholder': 'ادخل اسم مقهاك'}))
    location = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    social_media_link = forms.URLField(required=False, widget=forms.URLInput(attrs={'class': 'form-control'}))
    cafe_description = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}), required=False)
    cafe_logo = forms.ImageField(required=False, widget=forms.ClearableFileInput(attrs={'class': 'form-control-file'}))
    data_file = forms.FileField(required=False, widget=forms.ClearableFileInput(attrs={'class': 'form-control-file'}))
    firebase_config = forms.URLField(required=False, widget=forms.URLInput(attrs={'class': 'form-control'}))

    class Meta:
        model = UserProfile
        fields = ['cafe_name', 'location', 'area', 'city', 'social_media_link', 'cafe_description', 'cafe_logo', 'data_file', 'firebase_config']
        
    def save(self, commit=True):
        user_profile = super().save(commit=False)
        if commit:
            user_profile.save()
        return user_profile
