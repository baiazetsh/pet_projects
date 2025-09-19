#wether/views.py
import os
from django.shortcuts import render
import logging
from .api import fetch_weather
from django.conf import settings
from .models import WeatherCache
import json
from django.http import JsonResponse, HttpResponse
import csv

LOG_DIR = settings.BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)
logging.basicConfig(
    filename = LOG_DIR / "weather.log",
    level = logging.INFO,
    format = "%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def weather_view(request):
    city = request.GET.get('city', 'Flemington')
    weather_data = fetch_weather(city)

    cached = WeatherCache.objects.filter(city__iexact=city).order_by("-created_at").first()
    
    if cached and cached.is_fresh():
        weather_data = cached.as_dict()
    else:
        weather_data = fetch_weather(city)
        if "error" not in weather_data:
            WeatherCache.objects.create(
                city=city,
                data=json.dumps(weather_data)
            )

    if "error" in weather_data:
        logger.error(f"Wheather API error {city}: {weather_data['error']}")

        context ={
            'error': weather_data["error"],
            'city': city,
        }
        return render(request, 'weather/weather.html', context)
    else:
        logger.info(
            f"Weather data fetched successfully for {city}: temp {weather_data.get('main', {}).get('temp', 'N/A')}°C")

        context ={
            'weather': weather_data,
            'city': city,
            "api_key": settings.GOOGLE_MAPS_API_KEY 
        }
        return render(request, "weather/weather.html", context)

def export_json(request):
    city = request.GET.get("city", "Flemington")
    cached = WeatherCache.objects.filter(city__iexact=city).order_by("-created_at").first()
    if not cached:
        return JsonResponse({"error": "No cached data"}, status=404)
    return JsonResponse(cached.as_dict())

def export_csv(request):
    city = request.GET.get("city", "Flemington")
    cached = WeatherCache.objects.filter(city__iexact=city).order_by("-created_at").first()
    if not cached:
        return HttpResponse("No cached data", status=404)

    data = cached.as_dict()
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="{city}_weather.csv"'

    writer = csv.writer(response)
    writer.writerow(["City", "Temp", "humidity", "Wind", "Description"])
    writer.writerow([
        city,
        data["main"]["temp"],
        data["main"]["humidity"],
        data["wind"]["speed"],
        data["weather"][0]["description"]
    ])
    return response