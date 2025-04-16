from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from .models import UserProfile,City,Area
from django.utils.translation import gettext_lazy as _ 
from django.core.validators import FileExtensionValidator
from promotions.models import Event  




#مثل ماتلاحظون هذي فورم جديد انهرت من الاصليه حقت جانقو ليه سوينا كذا؟ عشان نقدر نحكم بالاتربيوت الي نبيهم زي مثلا هنا زدت الايميل! 
class CreateUser(UserCreationForm):
    email = forms.EmailField(required=True)
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
        return user
    
#هذي فورم حقت الستينقز والتعديلات المفروض ترتبط بالمودل (الي ماسويناه للحين) 
class UserProfileForm(forms.ModelForm):
    
    area = forms.ModelChoiceField(queryset=Area.objects.all(), empty_label=_("choose"), widget=forms.Select(attrs={'id': 'inputState5' ,'class':"form-control"}))
    city = forms.ModelChoiceField(queryset=City.objects.all(), empty_label=_("choose"), widget=forms.Select(attrs={'id': 'inputCity', 'class':"form-control"}))
 
    cafe_name = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={'class': 'form-control','placeholder': _('Enter your cafe name')}))
    location = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder':'example locatin'}))
    social_media_link = forms.URLField(required=False, widget=forms.URLInput(attrs={'class': 'form-control'}))
    cafe_description = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control','rows': 2}), required=False)
    cafe_logo = forms.ImageField(required=False, widget=forms.ClearableFileInput(attrs={'class': 'form-control-file', 'accept': '.png, .jpg, .jpeg, .gif, .webp'}),validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif', 'webp'])])    
    data_file = forms.FileField(widget=forms.ClearableFileInput(attrs={'class': 'form-control-file','accept': '.csv, .xlsx, .xls' }), validators=[FileExtensionValidator(allowed_extensions=['csv','.xlsx','.xls'])]) # the accept allows only csv at the frontend they cant chose a non csv, the validator prevents uploading non csv files)
    firebase_config = forms.URLField(required=False, widget=forms.URLInput(attrs={'class': 'form-control'}))
    class Meta:
        model = UserProfile
        fields = ['cafe_name', 'location', 'area', 'city', 'social_media_link', 'cafe_description', 'cafe_logo', 'data_file', 'firebase_config']
    
    # def clean_data_file(self): # هذي لو نبي مره نأمن رفع الملف انه بس ملف اكسل نقدر نحطها حماية باك اند 
    #     file = self.cleaned_data.get('data_file', False)
    #     if file:
    #         if not file.name.endswith('.csv'):
    #             raise forms.ValidationError("Only CSV files are allowed.")
    #     return file
 
    def save(self, commit=True):
        user_profile = super().save(commit=False)   
        if commit:
            user_profile.save()
        return user_profile


class UserUpdateForm(UserChangeForm):
    password=None # for security we hide it 
    email = forms.EmailField(required=True)
    class Meta:
        model = User
        fields = ['username', 'email']
    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
        return user
  
  