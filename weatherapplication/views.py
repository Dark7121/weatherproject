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
        
def search_result(request):
    report = {}
    forecast_data = {}
    historical_data = {}
    show_popup = False
    search_hour = 0
    
    if request.method == 'POST':
        city_name = request.POST.get('city')
    else:
        try:
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
    return render(request, 'signup.html')

def login(request):
    return render(request, 'login.html') 

def feedback(request):
    return render(request, 'feedbackform.html')   