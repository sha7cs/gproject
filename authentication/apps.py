from django.apps import AppConfig


class AuthenticationAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "authentication"
    
    # def ready(self):
    #     import authentication_app.signals   #هذي بس عشان يتعرف على السيقنالز لان حنا الي سوينا الملف مو موجود اوريدي
