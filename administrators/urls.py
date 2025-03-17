from django.urls import path
from . import views

urlpatterns = [
    # path('', views.index , name="admins.base"),
    path('', views.users , name="admins.users"),
    path('user/<int:user_id>/', views.user_details, name='user_details'),
    path('accept-user/<int:user_id>/', views.accept_user, name='accept_user'),
    path('remove_user/<int:user_id>/', views.remove_user, name='remove_user'),
    path('chat-control/', views.chat_control , name="admins.chatbot"),
    path('create-question/<int:subcategory_id>/', views.create_question, name='create_question'),
    path('delete-question/<int:question_id>/', views.delete_question, name='delete_question'),
    path('create-subcategory/<int:category_id>/', views.create_subcategory, name='create_subcategory'),
]