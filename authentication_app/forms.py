from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile


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
    class Meta:
        model = UserProfile
        fields = ['cafe_name', 'data_file', 'firebase_config'] 

