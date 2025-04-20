# config/urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    # Admin interface
    path('admin/', admin.site.urls),
    
    # JWT authentication endpoints
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Your app URLs
    path('api/data-collection/', include('apps.data_collection.api.urls')),
    path('api/text-processing/', include('apps.text_processing.api.urls')),
    path('api/entity-recognition/', include('apps.entity_recognition.api.urls')),
    path('api/sentiment-analysis/', include('apps.sentiment_analysis.api.urls')),
    path('api/trend-analysis/', include('apps.trend_analysis.api.urls')),
    
    # Old app URLs (if they exist)
    path('api/accountss/', include('accountss.urls')),
]