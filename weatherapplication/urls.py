from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('current', views.current_weather, name='current weather'),
    path('forecast', views.weather_forecast, name='forecast weather'),
    path('historical', views.historical_weather, name='historical weather'),
    path('sign-up', views.signup, name='signup'),
    path('log-in', views.login, name='login'),
    path('search', views.search_result, name='search'),
    path('feedback', views.feedback, name='feedback'),
    path('submit_feedback/', views.submit_feedback, name='submit_feedback'),
]