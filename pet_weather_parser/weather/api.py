# weather/api.py
import requests
from django.conf import settings


api_key = settings.WEATHER_API_KEY

BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

def fetch_weather(city_name: str, units: str="metric", lang: str="en") -> dict:
    params = {
        "q": city_name,
        "appid": settings.WEATHER_API_KEY,
        "units": units,
        "lang": lang,
    }

    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if str(data.get("cod")) != "200":
            return{"error": data.get("message", "Unknown API error")}

        return data
        
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

    except ValueError:
        return {"error": f"Invalid response from API: {response.text[:200]}"}
    