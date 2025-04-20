# apps/trend_analysis/api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TopicViewSet, TrendViewSet, AnalyticsResultViewSet

router = DefaultRouter()
router.register(r'topics', TopicViewSet)
router.register(r'trends', TrendViewSet)
router.register(r'analytics', AnalyticsResultViewSet)

urlpatterns = [
    path('', include(router.urls)),
]