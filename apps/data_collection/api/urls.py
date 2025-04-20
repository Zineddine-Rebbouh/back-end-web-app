# apps/data_collection/api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CollectDataView

router = DefaultRouter()

urlpatterns = [
    path('collect/', CollectDataView.as_view(), name='collect_data'),  # Fixed: Added .as_view()
    path('', include(router.urls)),
]