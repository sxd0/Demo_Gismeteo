from django.urls import path
from . import views

urlpatterns = [
    path('', views.weather_view, name='weather_view'),
    path('api/history/', views.search_count_api, name='search_count_api'),
]
