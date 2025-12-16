# 🌤️ Weatherly v2.0

**Weatherly** is a modern, cross-platform desktop weather application built with **PyQt5**, focused on clean UI design, smooth interactions, and practical weather information — without overwhelming the user.

It is designed to feel *native*, responsive, and visually polished while remaining lightweight and easy to use.

---

## 📸 Screenshots

**Main dashboard with dynamic weather background (sidebar collapsed)**  
![Main Window](https://github.com/user-attachments/assets/e47c527c-ee4d-4472-9572-804fc534729f)

**Saved cities and navigation (sidebar expanded)**  
![Main Window with Sidebar](https://github.com/user-attachments/assets/04175f60-3a86-4f7c-853f-b9f05e99aeab)

**Integrated weather-related news feed**  
![News Section](https://github.com/user-attachments/assets/91e2f03a-67b4-4949-acf4-f89131e44898)

**Settings and customization options**  
![Settings Page](https://github.com/user-attachments/assets/9f6d4aa6-a508-4f67-ba12-3330fedd9b1a)

---

## 🧠 Design Philosophy

Weatherly was built with three guiding principles:

- **Clarity over clutter** — show useful data without overwhelming the UI  
- **Responsiveness** — no freezing or blocking, even on slow networks  
- **Visual polish** — smooth animations and consistent styling throughout  

The goal is a desktop weather app that feels modern and pleasant to use, rather than purely utilitarian.

---

## ✨ Features

### 🎨 User Interface
- Modern dark theme optimized for long usage
- Dynamic backgrounds based on current weather conditions
- Smooth animations using cubic easing
- Collapsible, animated sidebar for saved locations
- Responsive layout that adapts to window resizing
- Subtle hover states and interaction feedback

### 🌍 Weather Data
- Real-time current weather:
  - Temperature and “feels like”
  - Humidity, pressure, wind speed & direction
  - Cloud cover, visibility, precipitation
  - Sunrise and sunset times
- 5-day weather forecast with icons
- Unlimited saved cities
- Automatic refresh (manual, 15 min, 30 min, 1 hour)
- Optional IP-based location detection

### 📰 Weather News
- Location-specific weather-related news
- Smart filtering to avoid unrelated articles
- Configurable number of articles (5 / 10 / 15)
- Relative timestamps (e.g., “2 days ago”)
- One-click access to full articles

### ⚙️ Customization
- Units:
  - Temperature (°C / °F)
  - Wind speed (m/s / mph)
  - Pressure (hPa / inHg)
  - Precipitation (mm / in)
- Display options:
  - 12h / 24h time format
  - Default startup city
  - Sidebar default state
- Privacy:
  - Optional location services
  - All data stored locally
  - No analytics or tracking

### 🛠️ Technical Highlights
- Cross-platform support (macOS & Windows)
- Platform-specific window sizing and behavior
- Background API calls using threads (non-blocking UI)
- Persistent local storage using JSON
- Graceful handling of network and API errors
- Powered by OpenWeatherMap

---

## 🚀 Installation

### Requirements
- Python **3.7+**
- `pip`

### Quick Start
```bash
git clone https://github.com/TRX-1000/Weatherly-v2.git
cd Weatherly-v2
pip install -r requirements.txt
python main.py
```

### Recommended: Virtual Environment

```bash
python3 -m venv venv   # On Windows: python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

---

## 🎯 First-Time Usage

1. Launch the app using `python main.py`
2. Your location can be auto-detected (optional)
3. Search for a city using the search bar
4. Cities are saved automatically in the sidebar
5. Click any city to switch instantly
6. Open settings (⚙️) to customize units and behavior

---

## 🧭 Controls

| Action | Method |
|------|------|
| Toggle sidebar | ☰ menu button |
| Search city | Enter city name + Enter |
| Refresh data | ↻ refresh button |
| Detect location | 📍 button |
| Open settings | ⚙️ button |
| Remove city | Right-click city card |

---

## ⚙️ Configuration

### `settings.json`
```json
{
  "temperature_unit": "celsius",
  "wind_unit": "metric",
  "pressure_unit": "hpa",
  "precipitation_unit": "mm",
  "time_format": "24h",
  "auto_refresh": true,
  "refresh_interval": "15",
  "default_city": "London",
  "news_count": "10",
  "sidebar_default": "expanded",
  "location_services": "enabled"
}
```

---

## 🔑 API Configuration

Weatherly uses **OpenWeatherMap**.

To use your own API key:
1. Open `main_window.py`
2. Replace:
```python
WeatherAPI("YOUR_API_KEY")
```
with your personal API key.

> A default key is included for convenience, but using your own key is recommended for long-term use.

---

## 🗂️ Project Structure

```
Weatherly-v2/
├── main.py
├── requirements.txt
├── ui/
├── tools/
├── assets/
└── settings.json
```

---

## 🗺️ Roadmap

- Hourly forecast
- Weather alerts
- Weather radar
- Historical data
- Multiple themes
- AQI & UV index
- Graphs & trends
- System tray integration

---

## 📝 License

Licensed under the **MIT License**.

---

### ⭐ If you find Weatherly useful, consider starring the repository
