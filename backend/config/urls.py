from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# API Documentation
schema_view = get_schema_view(
   openapi.Info(
      title="Pitch Perfect API",
      default_version='v1',
      description="API for Pitch Perfect AI coaching platform",
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='api-docs'),
    
    # API endpoints
    path('api/auth/', include('apps.accounts.urls')),
    path('api/pitches/', include('apps.pitches.urls')),
    path('api/practice/', include('apps.practice.urls')),
    path('api/qa/', include('apps.qa.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)