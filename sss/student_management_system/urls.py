from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from student_management_system import settings
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('student_management_app.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('api/', include('student_management_app.api_urls')),  # Add this line to include auth URLs
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
