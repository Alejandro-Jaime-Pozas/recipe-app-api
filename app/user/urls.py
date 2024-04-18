"""
URL mappings for the user API.
"""
from django.urls import path

from user import views

# this app_name is used as reference in main app's urls.py
app_name = 'user'

urlpatterns = [
    path('create/', views.CreateUserView.as_view(), name='create'),
    path('token/', views.CreateTokenView.as_view(), name='token'),
    path('me/', views.ManageUserView.as_view(), name='me'),
]
