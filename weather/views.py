from django.shortcuts import render, redirect
from .forms import CityForm
from .models import City, SearchHistory
from django.contrib.auth.decorators import login_required
import requests
from datetime import datetime, timedelta
import pytz
from django.http import JsonResponse
from django.db.models import Count, Sum

def get_weather(city_name):
    geocode_url = f'https://api.opencagedata.com/geocode/v1/json?q={city_name}&key=37962a5cce8b40688159b196f5ff5852'
    geocode_response = requests.get(geocode_url)
    if geocode_response.status_code == 200:
        geocode_data = geocode_response.json()
        if geocode_data['results']:
            latitude = geocode_data['results'][0]['geometry']['lat']
            longitude = geocode_data['results'][0]['geometry']['lng']
        else:
            return None
    else:
        return None

    api_url = f'https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&hourly=temperature_2m&timezone=Europe%2FMoscow&forecast_days=1'
    response = requests.get(api_url)
    if response.status_code == 200:
        weather_data = response.json()
        now = datetime.now(pytz.timezone('Europe/Moscow'))
        hourly_data = [
            (datetime.fromisoformat(time).replace(tzinfo=pytz.timezone('Europe/Moscow')), temp)
            for time, temp in zip(weather_data['hourly']['time'], weather_data['hourly']['temperature_2m'])
            if now <= datetime.fromisoformat(time).replace(tzinfo=pytz.timezone('Europe/Moscow')) < now + timedelta(hours=12)
        ]
        return hourly_data
    return None

@login_required
def weather_view(request):
    if request.method == 'POST':
        form = CityForm(request.POST)
        if form.is_valid():
            city_name = form.cleaned_data['city_name']
            weather_data = get_weather(city_name)
            
            if weather_data:
                city, created = City.objects.get_or_create(name=city_name)
                history, created = SearchHistory.objects.get_or_create(user=request.user, city=city)
                history.search_count += 1
                history.save()

                return render(request, 'weather/weather.html', {'weather_data': weather_data, 'form': form, 'city': city})
            else:
                return render(request, 'weather/weather.html', {'error': 'Could not retrieve weather data. Please try again later.', 'form': form})

    else:
        form = CityForm()

    last_search = SearchHistory.objects.filter(user=request.user).order_by('-last_searched').first()
    return render(request, 'weather/index.html', {'form': form, 'last_search': last_search})

@login_required
def search_count_api(request):
    history = SearchHistory.objects.filter(user=request.user).values('city__name').annotate(search_count=Sum('search_count'))
    return JsonResponse(list(history), safe=False)
