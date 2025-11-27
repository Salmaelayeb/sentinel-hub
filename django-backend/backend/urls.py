"""
URL configuration for security monitoring backend.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('security_api.urls')),
]
