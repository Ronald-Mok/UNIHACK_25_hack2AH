from django.contrib import admin # type: ignore
from django.urls import path, include # type: ignore


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('auth_app.urls')),  # Ensure this includes auth_app URLs

]
