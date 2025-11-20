import requests


class WeatherAPI:
    BASE_URL = "https://api.openweathermap.org/data/2.5"
    
    def __init__(self, api_key):
        self.api_key = api_key

    # -------------------------------
    # CURRENT WEATHER
    # -------------------------------
    def get_current_weather(self, city):
        """
        Returns current weather for a given city.
        (Temperature, description, feels-like, humidity, wind)
        """
        url = f"{self.BASE_URL}/weather?q={city}&appid={self.api_key}"

        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            return {
                "city": data["name"],
                "temp": data["main"]["temp"] - 273.15,
                "feels_like": data["main"]["feels_like"] - 273.15,
                "humidity": data["main"]["humidity"],
                "wind": data["wind"]["speed"],
                "description": data["weather"][0]["description"],
                "weather_id": data["weather"][0]["id"]
            }

        except Exception:
            return None

    # -------------------------------
    # 5 DAY / 3 HOUR FORECAST
    # -------------------------------
    def get_5day_forecast(self, city):
        """
        Returns raw 5-day forecast (3-hour data).
        We'll process it later inside UI classes.
        """
        url = f"{self.BASE_URL}/forecast?q={city}&appid={self.api_key}"

        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()["list"]
        except Exception:
            return None
