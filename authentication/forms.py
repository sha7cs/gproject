from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from .models import UserProfile,City,Area
from django.utils.translation import gettext_lazy as _ 
from django.core.validators import FileExtensionValidator
from promotions.models import Event  
from django.core.exceptions import ValidationError
import pandas as pd
import io
from django.core.files.base import ContentFile


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
    
class UserProfileForm(forms.ModelForm): 
   
    area = forms.ModelChoiceField(queryset=Area.objects.all(), empty_label=_("choose"), widget=forms.Select(attrs={'id': 'inputState5' ,'class':"form-control"}))
    city = forms.ModelChoiceField(queryset=City.objects.all(), empty_label=_("choose"), widget=forms.Select(attrs={'id': 'inputCity', 'class':"form-control"}))
    cafe_name = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control','placeholder': _('Enter your cafe name')}))
    cafe_name_ar = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control','placeholder': _('Enter your cafe name in Arabic')}))
    location = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder':'example locatin'}))
    social_media_link = forms.URLField(required=False, widget=forms.URLInput(attrs={'class': 'form-control'}))
    cafe_description = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control','rows': 2}), required=False)
    cafe_logo = forms.ImageField(required=False, widget=forms.ClearableFileInput(attrs={'class': 'form-control-file', 'accept': '.png, .jpg, .jpeg, .gif, .webp'}),validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif', 'webp'])])    
    data_file = forms.FileField(widget=forms.ClearableFileInput(attrs={'class': 'form-control-file','accept': '.csv' }), validators=[FileExtensionValidator(allowed_extensions=['csv'])]) # the accept allows only csv at the frontend they cant chose a non csv, the validator prevents uploading non csv files)
    firebase_config = forms.URLField(required=False, widget=forms.URLInput(attrs={'class': 'form-control'}))
    class Meta:
        model = UserProfile
        fields = ['cafe_name','cafe_name_ar', 'location', 'area', 'city', 'social_media_link', 'cafe_description', 'cafe_logo', 'data_file', 'firebase_config']
        

    def clean_data_file(self):
        uploaded = self.cleaned_data.get('data_file')
        if not uploaded:
            return None

        try:
            text = uploaded.read().decode('utf-8')
            df = pd.read_csv(io.StringIO(text))
        except Exception:
            raise ValidationError(_("The file is not a valid CSV or contains unsupported encoding."))

        # ✨ حوّل أسماء الأعمدة إلى lowercase
        df.columns = [col.strip().lower() for col in df.columns]

        # ✨ خريطة الأسماء البديلة
        column_aliases = {
            'id': ['id', 'ID', 'Id', 'receipt_id'],
            'branch_name': ['branch_name', 'branch', 'store'],
            'type': ['type', 'order_type'],
            'business_date': ['business_date', 'date', 'order_date'],
            'total_price': ['total_price', 'total', 'amount'],
            'detailed_orders': ['detailed_orders', 'orders', 'details'],
        }

        for standard_name, possible_names in column_aliases.items():
            for name in possible_names:
                if name.lower() in df.columns and name.lower() != standard_name:
                    df.rename(columns={name.lower(): standard_name}, inplace=True)
                    break

        # تحقق من الأعمدة الضرورية
        required = list(column_aliases.keys())
        missing = [c for c in required if c not in df.columns]
        if missing:
            raise ValidationError(
                _("Missing required columns: %(cols)s"),
                params={'cols': ", ".join(missing)}
            )

        # أضف الأعمدة الاختيارية بقيم نل لو مو موجودة
        optional = [
            'discount_name', 'discounts', 'total_taxes',
            'check_number', 'kitchen_notes',
            'preparation_period',
        ]
        for c in optional:
            if c not in df.columns:
                df[c] = pd.NA

        self.cleaned_data['dataframe'] = df

        # حفظ الملف المعدل بدلاً من الأصلي
        buffer = io.StringIO()
        df.to_csv(buffer, index=False)
        buffer.seek(0)
        new_file = ContentFile(buffer.read().encode('utf-8'), name=uploaded.name)

        return new_file
    
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
  
  