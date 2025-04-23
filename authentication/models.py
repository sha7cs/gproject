from django.db import models
from django.contrib.auth.models import User

#هنا هذا المودل زياده على الاساسي الي من جانقو عشان ندخل المعلومات الي ببالنا، ميزه ذي الطريقه انه تضمن الامان بالاوثنتكيشن بارت والايرورز
# وكل الاشياء ذي وبعدين اللي حنا مسوينه يعطينا حريتنا بالمعلمومات الي نحتاجه


class Area(models.Model): 
    class Meta:
        db_table = 'authentication_area'      
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class City(models.Model):  
    class Meta:
        db_table = 'authentication_city'
    name = models.CharField(max_length=255)
    area = models.ForeignKey(Area, on_delete=models.CASCADE, related_name="cities")

    def __str__(self):
        return f"{self.name} ({self.area.name})"
    
class UserProfile(models.Model):
    class Meta:
        db_table = 'authentication_userprofile'
    PENDING = 0
    ACCEPTED = 1
    DENIED = 2
    
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (ACCEPTED, 'Accepted'),
        (DENIED, 'Denied'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Links to User model
    cafe_name = models.CharField(max_length=255)  # Cafe name
    cafe_name_ar = models.CharField(max_length=255,blank=True, null=True)  # Cafe name in arabic 
    data_file = models.FileField(upload_to='static/uploads/' )  # Upload CSV or any file
    firebase_config = models.URLField(blank=True, null=True)  # Firebase Config link
    status = models.IntegerField(choices=STATUS_CHOICES, default=PENDING)  # Default to pending
    # New fields
    location = models.CharField(max_length=255, default='Filler' )
    area = models.ForeignKey(Area, on_delete=models.CASCADE)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    social_media_link = models.URLField(blank=True, null=True)  
    cafe_description = models.TextField(blank=True, null=True)  
    cafe_logo = models.ImageField(upload_to='static/logos/', blank=True, null=True)
    
    last_updated = models.DateTimeField(auto_now=True)

    def get_status_display_ar(self):
        """Returns the Arabic translation of the status."""
        translations = {
            self.PENDING: "قيد الانتظار",
            self.ACCEPTED: "مقبول",
            self.DENIED: "مرفوض"
        }
        return translations.get(self.status, "غير معروف")  # Default to "Unknown"
    
    def __str__(self):
        return self.user.username 