from django.urls import path
from . import views

urlpatterns = [
    path('sports/', views.SportsList.as_view(), name='sports-list'),
    path('entities/', views.EntitiesList.as_view(), name='entities-list'),  # Already correct
    path('trends/', views.TrendsList.as_view(), name='trends-list'),
    path('sentiments/', views.SentimentsList.as_view(), name='sentiments-list'),  # Ensure this is here
]