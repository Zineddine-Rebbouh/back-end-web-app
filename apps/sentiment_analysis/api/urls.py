# apps/sentiment_analysis/api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SentimentAnalysisViewSet, EntitySentimentViewSet

router = DefaultRouter()
router.register(r'document', SentimentAnalysisViewSet)
router.register(r'entity', EntitySentimentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]