from django.urls import path # type: ignore
# from .views import home
from django.urls import path # type: ignore
from .views import google_login, google_callback  # type: ignore # Import the views for Google OAuth

urlpatterns = [
    # path('login/', name='login'),  # Ensure this is defined correctly
    # path('', home, name='home'),
    path('auth/google/', google_login, name='google_login'),
    path('auth/callback/', google_callback, name='google_callback'),
]
