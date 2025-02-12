from django.db import models
from django.contrib.auth.models import User

#هنا هذا المودل زياده على الاساسي الي من جانقو عشان ندخل المعلومات الي ببالنا، ميزه ذي الطريقه انه تضمن الامان بالاوثنتكيشن بارت والايرورز
# وكل الاشياء ذي وبعدين اللي حنا مسوينه يعطينا حريتنا بالمعلمومات الي نحتاجه
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Links to User model
    cafe_name = models.CharField(max_length=255, blank=True, null=True)  # Cafe name
    data_file = models.FileField(upload_to='uploads/', blank=True, null=True)  # Upload CSV or any file
    firebase_config = models.URLField(blank=True, null=True)  # Firebase Config link

    def __str__(self):
        return self.user.username  # Display username in admin
