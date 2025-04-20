# apps/text_processing/api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProcessedDataViewSet  # From previous code

router = DefaultRouter()
router.register(r'processed', ProcessedDataViewSet)

urlpatterns = [
    path('', include(router.urls)),
]