from django.shortcuts import render
import requests
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.urls import reverse
from .models import Login, Feedback
from decouple import config
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
import re


NEW_API = '409bbc3d16674decb50192843230708'
date = datetime.now()
unix_timestamp = int(date.timestamp())
one_day = timedelta(days=1)
yesterday_datetime = date - one_day


# Replace 'YOUR_API_KEY' with your actual Bing Maps API key
api_key = 'ApEFJbsP80O3z2cagdSCN-WUU-hkUk2HFiovKL1XlgLQ4VXHQcR3QM-i2avw85AH'

def get_location_info(latitude, longitude, api_key):
    base_url = "http://dev.virtualearth.net/REST/v1/Locations/{point}"
    
    params = {
        'includeEntityTypes': 'Address,Postcode1,AdminDivision1,AdminDivision2,CountryRegion',
        'verboseplacenames': 'true',
        'key': api_key
    }
    
    url = base_url.format(point=f"{latitude},{longitude}")
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        resource_sets = data.get('resourceSets', [])
        
        if resource_sets:
            resources = resource_sets[0].get('resources', [])
            
            if resources:
                address = resources[0].get('address', {})
                city = address.get('locality')  # City
                district = address.get('adminDistrict2')  # District
                state = address.get('adminDistrict')  # State
                country = address.get('countryRegion')  # Country
                postcode = address.get('postalCode')  # Postcode1
                
                return {
                    'city': city,
                    'district': district,
                    'state': state,
                    'country': country,
                    'postcode': postcode
                }
    return None

#@login_required(login_url='/log-in')
def search_result(request):
    report = {}
    forecast_data = {}
    historical_data = {}
    show_popup = False
    search_hour = 0
    
    try:
        request.method == 'POST'
        city_name = request.POST.get('city')
    except (KeyError, ValueError):
        show_popup = True
        city_name = "Kolkata"

    if city_name:
        weather_url = f"https://api.weatherapi.com/v1/current.json?key={NEW_API}&q={city_name}&aqi=yes"
        try:
            response = requests.get(weather_url).json()
            report = {
                'city': response['location']['name'],
                'country': response['location']['country'],
                'date': response['location']['localtime'],
                'temp': response['current']['temp_c'],
                'feels_like': response['current']['feelslike_c'],
                'humidity': response['current']['humidity'],
                'wind': response['current']['wind_kph'],
                'description': response['current']['condition']['text'],
                'icon': response['current']['condition']['icon'],
            }
            report_date_str = report['date']
            report_date = datetime.strptime(report_date_str, '%Y-%m-%d %H:%M')
            search_hour = report_date.hour
        except (KeyError, ValueError):
            show_popup = True
            city_name = "Kolkata"
        except requests.exceptions.RequestException as e:
            print("Error making request:", e)
        except ValueError as e:
            print("Error decoding JSON:", e)

        forecast_url = f"http://api.weatherapi.com/v1/forecast.json?key={NEW_API}&q={city_name}&days=2&aqi=yes&alerts=yes"
        try:
            forecast_response = requests.get(forecast_url).json()
            forecast_data = {
                'f_date': forecast_response['forecast']['forecastday'][1]['hour'][search_hour]['time'],
                'f_temp': forecast_response['forecast']['forecastday'][1]['hour'][search_hour]['temp_c'],
                'f_humidity': forecast_response['forecast']['forecastday'][1]['hour'][search_hour]['humidity'],
                'f_feels_like': forecast_response['forecast']['forecastday'][1]['hour'][search_hour]['feelslike_c'],
                'f_icon': forecast_response['forecast']['forecastday'][1]['hour'][search_hour]['condition']['icon'],
                'f_wind': forecast_response['forecast']['forecastday'][1]['hour'][search_hour]['wind_kph'],
                'f_description': forecast_response['forecast']['forecastday'][1]['hour'][search_hour]['condition']['text'],
            }
        except requests.exceptions.RequestException as e:
            print("Error making request:", e)
        except ValueError as e:
            print("Error decoding JSON:", e)    
        
        historical_url = f"http://api.weatherapi.com/v1/history.json?key={NEW_API}&q={city_name}&dt={yesterday_datetime}"
        try:
            historical_response = requests.get(historical_url).json()
            historical_data = {
                'date': historical_response['forecast']['forecastday'][0]['hour'][search_hour]['time'],
                'temp': historical_response['forecast']['forecastday'][0]['hour'][search_hour]['temp_c'],
                'feels_like': historical_response['forecast']['forecastday'][0]['hour'][search_hour]['feelslike_c'],
                'humidity': historical_response['forecast']['forecastday'][0]['hour'][search_hour]['humidity'],
                'wind': historical_response['forecast']['forecastday'][0]['hour'][search_hour]['wind_kph'],
                'description': historical_response['forecast']['forecastday'][0]['hour'][search_hour]['condition']['text'],
                'sunrise': historical_response['forecast']['forecastday'][0]['astro']['sunrise'],
                'sunset': historical_response['forecast']['forecastday'][0]['astro']['sunset'],
                'moonrise': historical_response['forecast']['forecastday'][0]['astro']['moonrise'],
                'moonset': historical_response['forecast']['forecastday'][0]['astro']['moonset'],
                'moon_phase': historical_response['forecast']['forecastday'][0]['astro']['moon_phase'],
                'moon_illumination': historical_response['forecast']['forecastday'][0]['astro']['moon_illumination'],
                'weather_icon': historical_response['forecast']['forecastday'][0]['hour'][search_hour]['condition']['icon'],
            }
        except requests.exceptions.RequestException as e:
            print("Error making request:", e)
        except ValueError as e:
            print("Error decoding JSON:", e)
                  
    else:
        city_name = 'Kolkata'
        weather_url = f"https://api.weatherapi.com/v1/current.json?key={NEW_API}&q={city_name}&aqi=yes"
        try:
            response = requests.get(weather_url).json()
            report = {
                'city': response['location']['name'],
                'country': response['location']['country'],
                'date': response['location']['localtime'],
                'temp': response['current']['temp_c'],
                'feels_like': response['current']['feelslike_c'],
                'humidity': response['current']['humidity'],
                'wind': response['current']['wind_kph'],
                'description': response['current']['condition']['text'],
                'icon': response['current']['condition']['icon'],
            }
        except requests.exceptions.RequestException as e:
            print("Error making request:", e)
        except ValueError as e:
            print("Error decoding JSON:", e)
        report_date_str = report['date']
        report_date = datetime.strptime(report_date_str, '%Y-%m-%d %H:%M')
        search_hour = report_date.hour

        forecast_url = f"http://api.weatherapi.com/v1/forecast.json?key={NEW_API}&q={city_name}&days=2&aqi=yes&alerts=yes"
        try:
            forecast_response = requests.get(forecast_url).json()
            forecast_data = {
                'f_date': forecast_response['forecast']['forecastday'][1]['hour'][search_hour]['time'],
                'f_temp': forecast_response['forecast']['forecastday'][1]['hour'][search_hour]['temp_c'],
                'f_humidity': forecast_response['forecast']['forecastday'][1]['hour'][search_hour]['humidity'],
                'f_feels_like': forecast_response['forecast']['forecastday'][1]['hour'][search_hour]['feelslike_c'],
                'f_icon': forecast_response['forecast']['forecastday'][1]['hour'][search_hour]['condition']['icon'],
                'f_wind': forecast_response['forecast']['forecastday'][1]['hour'][search_hour]['wind_kph'],
                'f_description': forecast_response['forecast']['forecastday'][1]['hour'][search_hour]['condition']['text'],
            }
        except requests.exceptions.RequestException as e:
            print("Error making request:", e)
        except ValueError as e:
            print("Error decoding JSON:", e)    
        
        historical_url = f"http://api.weatherapi.com/v1/history.json?key={NEW_API}&q={city_name}&dt={yesterday_datetime}"
        try:
            historical_response = requests.get(historical_url).json()
            historical_data = {
                'date': historical_response['forecast']['forecastday'][0]['hour'][search_hour]['time'],
                'temp': historical_response['forecast']['forecastday'][0]['hour'][search_hour]['temp_c'],
                'feels_like': historical_response['forecast']['forecastday'][0]['hour'][search_hour]['feelslike_c'],
                'humidity': historical_response['forecast']['forecastday'][0]['hour'][search_hour]['humidity'],
                'wind': historical_response['forecast']['forecastday'][0]['hour'][search_hour]['wind_kph'],
                'description': historical_response['forecast']['forecastday'][0]['hour'][search_hour]['condition']['text'],
                'sunrise': historical_response['forecast']['forecastday'][0]['astro']['sunrise'],
                'sunset': historical_response['forecast']['forecastday'][0]['astro']['sunset'],
                'moonrise': historical_response['forecast']['forecastday'][0]['astro']['moonrise'],
                'moonset': historical_response['forecast']['forecastday'][0]['astro']['moonset'],
                'moon_phase': historical_response['forecast']['forecastday'][0]['astro']['moon_phase'],
                'moon_illumination': historical_response['forecast']['forecastday'][0]['astro']['moon_illumination'],
                'weather_icon': historical_response['forecast']['forecastday'][0]['hour'][search_hour]['condition']['icon'],
            }
        except requests.exceptions.RequestException as e:
            print("Error making request:", e)
        except ValueError as e:
            print("Error decoding JSON:", e)
    weather_report = {
        'report': report,
        'forecast_data': forecast_data,
        'historical_data': historical_data,
        'search_hour': search_hour,
        'show_popup': show_popup,
    }
    return render(request, 'search.html', weather_report)

def home(request):
    latitude = request.GET.get('latitude')
    longitude = request.GET.get('longitude')
    local_hour = request.GET.get('local_hour')
    if local_hour:
        local_hour = int(local_hour)
    else:
        local_hour = 0
    print(local_hour)
    report = {}
    historical_data = {}
    ci = {}
    if latitude and longitude:
        latitude = round(float(latitude), 2)
        longitude = round(float(longitude), 2)
        ci = get_location_info(latitude, longitude, api_key)

        weather_url = f"https://api.weatherapi.com/v1/current.json?key={NEW_API}&q={latitude},{longitude}&aqi=yes"
        try:
            response = requests.get(weather_url).json()
            report = {
            'date': response['location']['localtime'],
            'temp': response['current']['temp_c'],
            'feels_like': response['current']['feelslike_c'],
            'humidity': response['current']['humidity'],
            'wind': response['current']['wind_kph'],
            'description': response['current']['condition']['text'],
            'icon': response['current']['condition']['icon'],
            }
        except requests.exceptions.RequestException as e:
            print("Error making request:", e)
        except ValueError as e:
            print("Error decoding JSON:", e)
        
        forecast_url = f"http://api.weatherapi.com/v1/forecast.json?key={NEW_API}&q={latitude},{longitude}&days=2&aqi=yes&alerts=yes"
        try:
            forecast_response = requests.get(forecast_url).json()
            forecast_data = {
            'f_date': forecast_response['forecast']['forecastday'][1]['hour'][local_hour]['time'],
            'f_temp': forecast_response['forecast']['forecastday'][1]['hour'][local_hour]['temp_c'],
            'f_humidity': forecast_response['forecast']['forecastday'][1]['hour'][local_hour]['humidity'],
            'f_feels_like': forecast_response['forecast']['forecastday'][1]['hour'][local_hour]['feelslike_c'],
            'f_icon': forecast_response['forecast']['forecastday'][1]['hour'][local_hour]['condition']['icon'],
            'f_wind': forecast_response['forecast']['forecastday'][1]['hour'][local_hour]['wind_kph'],
            'f_description': forecast_response['forecast']['forecastday'][1]['hour'][local_hour]['condition']['text'],
            }
        except requests.exceptions.RequestException as e:
            print("Error making request:", e)
        except ValueError as e:
            print("Error decoding JSON:", e)
            
        
        historical_url = f"http://api.weatherapi.com/v1/history.json?key={NEW_API}&q={latitude},{longitude}&dt={yesterday_datetime}"
        try:
            historical_response = requests.get(historical_url).json()
            historical_data = {
                    'date': historical_response['forecast']['forecastday'][0]['hour'][local_hour]['time'],
                    'temp': historical_response['forecast']['forecastday'][0]['hour'][local_hour]['temp_c'],
                    'feels_like': historical_response['forecast']['forecastday'][0]['hour'][local_hour]['feelslike_c'],
                    'humidity': historical_response['forecast']['forecastday'][0]['hour'][local_hour]['humidity'],
                    'wind': historical_response['forecast']['forecastday'][0]['hour'][local_hour]['wind_kph'],
                    'description': historical_response['forecast']['forecastday'][0]['hour'][local_hour]['condition']['text'],
                    'sunrise': historical_response['forecast']['forecastday'][0]['astro']['sunrise'],
                    'sunset': historical_response['forecast']['forecastday'][0]['astro']['sunset'],
                    'moonrise': historical_response['forecast']['forecastday'][0]['astro']['moonrise'],
                    'moonset': historical_response['forecast']['forecastday'][0]['astro']['moonset'],
                    'moon_phase': historical_response['forecast']['forecastday'][0]['astro']['moon_phase'],
                    'moon_illumination': historical_response['forecast']['forecastday'][0]['astro']['moon_illumination'],
                    'weather_icon': historical_response['forecast']['forecastday'][0]['hour'][local_hour]['condition']['icon'],
                }
        except requests.exceptions.RequestException as e:
            print("Error making request:", e)
        except ValueError as e:
            print("Error decoding JSON:", e)
    
    
    else:
        latitude = 22.57
        longitude = 88.36
        ci = get_location_info(latitude, longitude, api_key)
        weather_url = f"https://api.weatherapi.com/v1/current.json?key={NEW_API}&q={latitude},{longitude}&aqi=yes"
        try:
            response = requests.get(weather_url).json()
            report = {
            'date': response['location']['localtime'],
            'temp': response['current']['temp_c'],
            'feels_like': response['current']['feelslike_c'],
            'humidity': response['current']['humidity'],
            'wind': response['current']['wind_kph'],
            'description': response['current']['condition']['text'],
            'icon': response['current']['condition']['icon'],
            }
        except requests.exceptions.RequestException as e:
            print("Error making request:", e)
        except ValueError as e:
            print("Error decoding JSON:", e)
        
        forecast_url = f"http://api.weatherapi.com/v1/forecast.json?key={NEW_API}&q={latitude},{longitude}&days=2&aqi=yes&alerts=yes"
        try:
            forecast_response = requests.get(forecast_url).json()
            forecast_data = {
            'f_date': forecast_response['forecast']['forecastday'][1]['hour'][local_hour]['time'],
            'f_temp': forecast_response['forecast']['forecastday'][1]['hour'][local_hour]['temp_c'],
            'f_humidity': forecast_response['forecast']['forecastday'][1]['hour'][local_hour]['humidity'],
            'f_feels_like': forecast_response['forecast']['forecastday'][1]['hour'][local_hour]['feelslike_c'],
            'f_icon': forecast_response['forecast']['forecastday'][1]['hour'][local_hour]['condition']['icon'],
            'f_wind': forecast_response['forecast']['forecastday'][1]['hour'][local_hour]['wind_kph'],
            'f_description': forecast_response['forecast']['forecastday'][1]['hour'][local_hour]['condition']['text'],
            }
        except requests.exceptions.RequestException as e:
            print("Error making request:", e)
        except ValueError as e:
            print("Error decoding JSON:", e)
            
        
        historical_url = f"http://api.weatherapi.com/v1/history.json?key={NEW_API}&q={latitude},{longitude}&dt={yesterday_datetime}"
        try:
            historical_response = requests.get(historical_url).json()
            historical_data = {
                    'date': historical_response['forecast']['forecastday'][0]['hour'][local_hour]['time'],
                    'temp': historical_response['forecast']['forecastday'][0]['hour'][local_hour]['temp_c'],
                    'feels_like': historical_response['forecast']['forecastday'][0]['hour'][local_hour]['feelslike_c'],
                    'humidity': historical_response['forecast']['forecastday'][0]['hour'][local_hour]['humidity'],
                    'wind': historical_response['forecast']['forecastday'][0]['hour'][local_hour]['wind_kph'],
                    'description': historical_response['forecast']['forecastday'][0]['hour'][local_hour]['condition']['text'],
                    'sunrise': historical_response['forecast']['forecastday'][0]['astro']['sunrise'],
                    'sunset': historical_response['forecast']['forecastday'][0]['astro']['sunset'],
                    'moonrise': historical_response['forecast']['forecastday'][0]['astro']['moonrise'],
                    'moonset': historical_response['forecast']['forecastday'][0]['astro']['moonset'],
                    'moon_phase': historical_response['forecast']['forecastday'][0]['astro']['moon_phase'],
                    'moon_illumination': historical_response['forecast']['forecastday'][0]['astro']['moon_illumination'],
                    'weather_icon': historical_response['forecast']['forecastday'][0]['hour'][local_hour]['condition']['icon'],
                }
        except requests.exceptions.RequestException as e:
            print("Error making request:", e)
        except ValueError as e:
            print("Error decoding JSON:", e)
        
            
        

    context = {
        'report': report,
        'forecast_data': forecast_data,
        'historical_data': historical_data,
        'ci': ci
    }
    
    return render(request, 'home.html', context)

def current_weather(request):
     
    return render(request, 'current_weather.html')


def historical_weather(request):
     
    return render(request, 'historical_weather.html')


def weather_forecast(request):
    
    return render(request, 'weather_forecast.html')

def signup(request):
    next_page = request.POST.get('next')
    password_pattern = (r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*()_\-+=]).{8,20}$')
    if request.method == 'POST':
        try:
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            confirmpassword = request.POST.get('confirmpassword')
            if password != confirmpassword:
                error_message = "Passwords do not match. Please try again."
                return render(request, 'signup.html', {'error_message': error_message})
            
            elif not re.match(password_pattern, password): 
                error_message = "Password must contain at least 1 uppercase letter, 1 lowercase letter, 1 digit, and 1 special character."
                return render(request, 'signup.html', {'error_message': error_message})
                
            elif User.objects.filter(Q(username__iexact=username)).exists() and Signup.objects.filter(Q(email__iexact=email)).exists():
                error_message = "Username and email both already exist. Please try again."
                return render(request, 'signup.html', {'error_message': error_message})

            elif User.objects.filter(Q(username__iexact=username)).exists():
                error_message = "Username already exists. Please try again."
                return render(request, 'signup.html', {'error_message': error_message})
                
            elif User.objects.filter(Q(email__iexact=email)).exists():
                error_message = "Email already exists. Please try again."
                return render(request, 'signup.html', {'error_message': error_message})
                
            else:
                User.objects.create_user(username=username, email=email, password=password)
                if next_page:
                    return redirect(next_page)
                else:
                    return redirect('login')
            
        except Exception as e:
            error_message = str(e)
            return render(request, 'signup.html', {'error_message': error_message})
    return render(request, 'signup.html')

def login_view(request):
    next_page = request.POST.get('next')
    if request.method == 'POST':
        try:
            usernameoremail = request.POST.get('usernameoremail') 
            password = request.POST.get('password')
            
            if '@' in usernameoremail:
                user = User.objects.filter(email=usernameoremail).first()
                if user:
                    user = authenticate(request, username=user.username, password=password)
            else:
                user = authenticate(request, username=usernameoremail, password=password)
                
            if user is not None:
                auth_login(request, user)
                if next_page:
                    return redirect(next_page)
                else:
                    return redirect('home')
            else:
                try:
                    user = User.objects.get(username=usernameoremail)
                    error_message = "Invalid Password. Please try again."
                except User.DoesNotExist:
                    error_message = "Invalid Username. Please try again."
                return render(request, 'login.html', {'error_message': error_message})

        except Exception as e:
            error_message = str(e)
            return render(request, 'login.html', {'error_message': error_message})
    return render(request, 'login.html') 

@login_required
def logout_view(request):
    logout(request)
    return redirect(reverse('home'))

def feedback(request):
    return render(request, 'feedbackform.html')

def submit_feedback(request):
    if request.method == 'POST':
        try:
            firstname = request.POST.get('firstname')
            lastname = request.POST.get('lastname')
            email = request.POST.get('email')
            message = request.POST.get('message')
            Feedback.objects.create(firstname=firstname, lastname=lastname, email=email, message=message)
            return redirect('/')
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})
