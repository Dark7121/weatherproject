from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
<<<<<<< HEAD
    path('current', views.current_weather, name='current weather'),
    path('forecast', views.weather_forecast, name='forecast weather'),
    path('historical', views.historical_weather, name='historical weather'),
    path('sign-up', views.signup, name='signup'),
    path('log-in', views.login, name='login'),
]
=======
]
>>>>>>> 121e4f5d84e68c0d1da06f55a5189a5460845850
