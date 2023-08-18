from django.shortcuts import render
import requests
from urllib import request
from datetime import datetime, timedelta
import pytz
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt


NEW_API = '409bbc3d16674decb50192843230708'
date = datetime.now()
hour_only = date.hour
fhour_only = date.hour + 24
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

'''
# current weather
if latitude and longitude:
    current_url = f"https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={API_KEY}&units=metric"
    try:
        response = requests.get(current_url).json()
        report = {
            'city': city_name,
            'country_code': response['sys']['country'],
            'cor': f"Lat: {response['coord']['lat']}, Lon: {response['coord']['lon']}",
            'temp': response['main']['temp'],
            'pressure': response['main']['pressure'],
            'humidity': response['main']['humidity'],
            'main': response['weather'][0]['main'],
            'description': response['weather'][0]['description'],
            'icon': response['weather'][0]['icon'],
        }
    except requests.exceptions.RequestException as e:
        print("Error making request:", e)
    except ValueError as e:
        print("Error decoding JSON:", e)
else:
    current_url = f"https://api.openweathermap.org/data/2.5/weather?q={city_name}&units=metric&appid={API_KEY}"
    try:
        response = requests.get(current_url).json()
        report = {
            'city': city_name,
            'country_code': response['sys']['country'],
            'cor': f"Lat: {response['coord']['lat']}, Lon: {response['coord']['lon']}",
            'temp': response['main']['temp'],
            'pressure': response['main']['pressure'],
            'humidity': response['main']['humidity'],
            'main': response['weather'][0]['main'],
            'description': response['weather'][0]['description'],
            'icon': response['weather'][0]['icon'],
        }
    except requests.exceptions.RequestException as e:
        print("Error making request:", e)
    except ValueError as e:
        print("Error decoding JSON:", e)
            
    
# historical weather
historical_url = f"http://api.weatherapi.com/v1/history.json?key={NEW_API}&q={city_name}&dt={yesterday_datetime}"
try:
        historical_response = requests.get(historical_url).json()
        historical_data = {
                    'date': historical_response['location']['localtime'],
                    'temp': historical_response['forecast']['forecastday'][0]['day']['avgtemp_c'],
                    'condition': historical_response['forecast']['forecastday'][0]['day']['condition']['text'],
                    'humidity': historical_response['forecast']['forecastday'][0]['day']['avghumidity'],
                    'wind': historical_response['forecast']['forecastday'][0]['day']['maxwind_kph'],
                    'sunrise': historical_response['forecast']['forecastday'][0]['astro']['sunrise'],
                    'sunset': historical_response['forecast']['forecastday'][0]['astro']['sunset'],
                    'moonrise': historical_response['forecast']['forecastday'][0]['astro']['moonrise'],
                    'moonset': historical_response['forecast']['forecastday'][0]['astro']['moonset'],
                    'moon_phase': historical_response['forecast']['forecastday'][0]['astro']['moon_phase'],
                    'moon_illumination': historical_response['forecast']['forecastday'][0]['astro']['moon_illumination'],
                    'weather_icon': historical_response['forecast']['forecastday'][0]['day']['condition']['icon'],
                }
except requests.exceptions.RequestException as e:
    print("Error making request:", e)
except ValueError as e:
    print("Error decoding JSON:", e)
    
    
# weather forecast
weather_forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?q={city_name}&appid={API_KEY}"
try:
        forecast_response = requests.get(weather_forecast_url).json()
        forecast_data = {
                    'date': forecast_response['list'][0]['dt'],
                    'temp': forecast_response['list'][0]['main']['temp'],
                    'humidity': forecast_response['list'][0]['main']['humidity'],
                    'feels_like': forecast_response['list'][0]['main']['feels_like'],
                    'icon': forecast_response['list'][0]['weather'][0]['icon'],
                }
except requests.exceptions.RequestException as e:
    print("Error making request:", e)
except ValueError as e:
    print("Error decoding JSON:", e)
'''

def home(request):
    latitude = request.GET.get('latitude')
    longitude = request.GET.get('longitude')
    report = {}
    historical_data = {}
    ci = {}
    
    if latitude and longitude:
        latitude = round(float(latitude), 2)
        longitude = round(float(longitude), 2)
        print(latitude, longitude)
        ci = get_location_info(latitude, longitude, api_key)
        weather_url = f"http://api.weatherapi.com/v1/forecast.json?key={NEW_API}&q={latitude},{longitude}&days=2&aqi=yes&alerts=yes"
        try:
            response = requests.get(weather_url).json()
            report = {
            'date': response['forecast']['forecastday'][0]['hour'][hour_only]['time'],
            'temp': response['forecast']['forecastday'][0]['hour'][hour_only]['temp_c'],
            'feels_like': response['forecast']['forecastday'][0]['hour'][hour_only]['feelslike_c'],
            'humidity': response['forecast']['forecastday'][0]['hour'][hour_only]['humidity'],
            'wind': response['forecast']['forecastday'][0]['hour'][hour_only]['wind_kph'],
            'description': response['forecast']['forecastday'][0]['hour'][hour_only]['condition']['text'],
            'icon': response['forecast']['forecastday'][0]['hour'][hour_only]['condition']['icon'],
        
            'f_date': response['forecast']['forecastday'][1]['hour'][hour_only]['time'],
            'f_temp': response['forecast']['forecastday'][1]['hour'][hour_only]['temp_c'],
            'f_humidity': response['forecast']['forecastday'][1]['hour'][hour_only]['humidity'],
            'f_feels_like': response['forecast']['forecastday'][1]['hour'][hour_only]['feelslike_c'],
            'f_icon': response['forecast']['forecastday'][1]['hour'][hour_only]['condition']['icon'],
            'f_wind': response['forecast']['forecastday'][1]['hour'][hour_only]['wind_kph'],
            'f_description': response['forecast']['forecastday'][1]['hour'][hour_only]['condition']['text'],
            }
        except requests.exceptions.RequestException as e:
            print("Error making request:", e)
        except ValueError as e:
            print("Error decoding JSON:", e)
            
        
        historical_url = f"http://api.weatherapi.com/v1/history.json?key={NEW_API}&q={latitude},{longitude}&dt={yesterday_datetime}"
        try:
            historical_response = requests.get(historical_url).json()
            historical_data = {
                    'date': historical_response['forecast']['forecastday'][0]['hour'][hour_only]['time'],
                    'temp': historical_response['forecast']['forecastday'][0]['hour'][hour_only]['temp_c'],
                    'feels_like': historical_response['forecast']['forecastday'][0]['hour'][hour_only]['feelslike_c'],
                    'humidity': historical_response['forecast']['forecastday'][0]['hour'][hour_only]['humidity'],
                    'wind': historical_response['forecast']['forecastday'][0]['hour'][hour_only]['wind_kph'],
                    'description': historical_response['forecast']['forecastday'][0]['hour'][hour_only]['condition']['text'],
                    'sunrise': historical_response['forecast']['forecastday'][0]['astro']['sunrise'],
                    'sunset': historical_response['forecast']['forecastday'][0]['astro']['sunset'],
                    'moonrise': historical_response['forecast']['forecastday'][0]['astro']['moonrise'],
                    'moonset': historical_response['forecast']['forecastday'][0]['astro']['moonset'],
                    'moon_phase': historical_response['forecast']['forecastday'][0]['astro']['moon_phase'],
                    'moon_illumination': historical_response['forecast']['forecastday'][0]['astro']['moon_illumination'],
                    'weather_icon': historical_response['forecast']['forecastday'][0]['hour'][hour_only]['condition']['icon'],
                }
        except requests.exceptions.RequestException as e:
            print("Error making request:", e)
        except ValueError as e:
            print("Error decoding JSON:", e)
    
    else:
        latitude = 22.57
        longitude = 88.36
        ci = get_location_info(latitude, longitude, api_key)
        current_url = f"http://api.weatherapi.com/v1/forecast.json?key={NEW_API}&q={latitude},{longitude}&days=2&aqi=yes&alerts=yes"
        try:
            response = requests.get(current_url).json()
            report = {
            'date': response['forecast']['forecastday'][0]['hour'][hour_only]['time'],
            'temp': response['forecast']['forecastday'][0]['hour'][hour_only]['temp_c'],
            'feels_like': response['forecast']['forecastday'][0]['hour'][hour_only]['feelslike_c'],
            'humidity': response['forecast']['forecastday'][0]['hour'][hour_only]['humidity'],
            'wind': response['forecast']['forecastday'][0]['hour'][hour_only]['wind_kph'],
            'description': response['forecast']['forecastday'][0]['hour'][hour_only]['condition']['text'],
            'icon': response['forecast']['forecastday'][0]['hour'][hour_only]['condition']['icon'],
        
            'f_date': response['forecast']['forecastday'][1]['hour'][hour_only]['time'],
            'f_temp': response['forecast']['forecastday'][1]['hour'][hour_only]['temp_c'],
            'f_humidity': response['forecast']['forecastday'][1]['hour'][hour_only]['humidity'],
            'f_feels_like': response['forecast']['forecastday'][1]['hour'][hour_only]['feelslike_c'],
            'f_icon': response['forecast']['forecastday'][1]['hour'][hour_only]['condition']['icon'],
            'f_wind': response['forecast']['forecastday'][1]['hour'][hour_only]['wind_kph'],
            'f_description': response['forecast']['forecastday'][1]['hour'][hour_only]['condition']['text'],
            }
        except requests.exceptions.RequestException as e:
            print("Error making request:", e)
        except ValueError as e:
            print("Error decoding JSON:", e)
            
        
        historical_url = f"http://api.weatherapi.com/v1/history.json?key={NEW_API}&q={latitude},{longitude}&dt={yesterday_datetime}"
        try:
            historical_response = requests.get(historical_url).json()
            historical_data = {
                    'date': historical_response['forecast']['forecastday'][0]['hour'][hour_only]['time'],
                    'temp': historical_response['forecast']['forecastday'][0]['hour'][hour_only]['temp_c'],
                    'feels_like': historical_response['forecast']['forecastday'][0]['hour'][hour_only]['feelslike_c'],
                    'humidity': historical_response['forecast']['forecastday'][0]['hour'][hour_only]['humidity'],
                    'wind': historical_response['forecast']['forecastday'][0]['hour'][hour_only]['wind_kph'],
                    'description': historical_response['forecast']['forecastday'][0]['hour'][hour_only]['condition']['text'],
                    'sunrise': historical_response['forecast']['forecastday'][0]['astro']['sunrise'],
                    'sunset': historical_response['forecast']['forecastday'][0]['astro']['sunset'],
                    'moonrise': historical_response['forecast']['forecastday'][0]['astro']['moonrise'],
                    'moonset': historical_response['forecast']['forecastday'][0]['astro']['moonset'],
                    'moon_phase': historical_response['forecast']['forecastday'][0]['astro']['moon_phase'],
                    'moon_illumination': historical_response['forecast']['forecastday'][0]['astro']['moon_illumination'],
                    'weather_icon': historical_response['forecast']['forecastday'][0]['hour'][hour_only]['condition']['icon'],
                }
        except requests.exceptions.RequestException as e:
            print("Error making request:", e)
        except ValueError as e:
            print("Error decoding JSON:", e)
        
            
        

    context = {
        'report': report,
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
    return render(request, 'signup.html')

def login(request):
    return render(request, 'login.html')    