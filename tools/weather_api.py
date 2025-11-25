import requests
from datetime import datetime


class WeatherAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5"

    # ---------------------------
    # Internal Request Handler
    # ---------------------------
    def _request(self, endpoint, params):
        params["appid"] = self.api_key
        try:
            r = requests.get(f"{self.base_url}/{endpoint}", params=params, timeout=10)
            r.raise_for_status()
            return r.json()
        except (requests.RequestException, ValueError) as e:
            print(f"API Error: {e}")
            return None

    # ---------------------------
    # Current Weather
    # ---------------------------
    def get_current_weather(self, city, units="metric"):
        data = self._request("weather", {"q": city, "units": units})
        if not data:
            return None

        w = data["weather"][0]
        m = data["main"]

        return {
            "city": data["name"],
            "country": data["sys"]["country"],
            "temperature": m["temp"],
            "feels_like": m["feels_like"],
            "temp_min": m["temp_min"],
            "temp_max": m["temp_max"],
            "humidity": m["humidity"],
            "pressure": m["pressure"],
            "description": w["description"],
            "main": w["main"],
            "icon": w["icon"],
            "id": w["id"],  # Added weather condition ID
            "wind_speed": data["wind"]["speed"],
            "wind_deg": data["wind"].get("deg", 0),
            "clouds": data["clouds"]["all"],
            "timestamp": data["dt"],
            "sunrise": data["sys"]["sunrise"],
            "sunset": data["sys"]["sunset"],
            "timezone": data["timezone"]
        }

    # ---------------------------
    # 5-Day / 3-Hour Forecast
    # ---------------------------
    def get_5day_forecast(self, city, units="metric"):
        data = self._request("forecast", {"q": city, "units": units})
        if not data:
            return None

        forecast_by_day = {}

        for item in data["list"]:
            ts = item["dt"]
            date = datetime.fromtimestamp(ts).strftime("%Y-%m-%d")

            if date not in forecast_by_day:
                forecast_by_day[date] = []

            w = item["weather"][0]
            m = item["main"]

            forecast_by_day[date].append({
                "time": datetime.fromtimestamp(ts).strftime("%H:%M"),
                "timestamp": ts,
                "temperature": m["temp"],
                "feels_like": m["feels_like"],
                "temp_min": m["temp_min"],
                "temp_max": m["temp_max"],
                "humidity": m["humidity"],
                "pressure": m["pressure"],
                "description": w["description"],
                "main": w["main"],
                "icon": w["icon"],
                "id": w["id"],  # Added weather condition ID
                "wind_speed": item["wind"]["speed"],
                "wind_deg": item["wind"].get("deg", 0),
                "clouds": item["clouds"]["all"],
                "pop": item.get("pop", 0) * 100
            })

        return {
            "city": data["city"]["name"],
            "country": data["city"]["country"],
            "forecast": forecast_by_day
        }

    # ---------------------------
    # Daily Summary
    # ---------------------------
    def get_daily_summary(self, city, units="metric"):
        forecast_data = self.get_5day_forecast(city, units)
        if not forecast_data:
            return None

        summaries = []

        for date, blocks in forecast_data["forecast"].items():
            temps = [b["temperature"] for b in blocks]
            mid = blocks[len(blocks) // 2]  # mid-block → closest to midday

            summaries.append({
                "date": date,
                "day_name": datetime.strptime(date, "%Y-%m-%d").strftime("%A"),
                "temp_min": min(temps),
                "temp_max": max(temps),
                "temp_avg": sum(temps) / len(temps),
                "description": mid["description"],
                "icon": mid["icon"],
                "id": mid["id"],  # Added weather condition ID
                "humidity": sum(b["humidity"] for b in blocks) / len(blocks),
                "wind_speed": sum(b["wind_speed"] for b in blocks) / len(blocks),
            })

        return {
            "city": forecast_data["city"],
            "country": forecast_data["country"],
            "daily": summaries
        }