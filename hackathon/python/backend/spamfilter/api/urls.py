from django.urls import path # type: ignore
from .views import google_login, google_callback  # type: ignore # Import the views for Google OAuth

urlpatterns = [
    path('auth/google/', google_login, name='google_login'),
    path('auth/callback/', google_callback, name='google_callback'),
]