# 🌤️ Weatherly v2.0

<div align="center">

![Weatherly Banner](https://img.shields.io/badge/Weatherly-v2.0-4a8fff?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.7+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PyQt5](https://img.shields.io/badge/PyQt5-Latest-41CD52?style=for-the-badge&logo=qt&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

**A sleek, modern weather application built with PyQt5 featuring a beautiful dark UI, smooth animations, and comprehensive weather data**

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Screenshots](#-screenshots) • [Configuration](#%EF%B8%8F-configuration) • [Easter Eggs](#-easter-eggs) • [Contributing](#-contributing) • [License](#-license)

</div>

---

## ✨ Features

### 🎨 **Beautiful UI/UX**
- **Modern Dark Theme** - Eye-friendly dark interface with glassmorphic design elements
- **Dynamic Backgrounds** - Weather-aware backgrounds that change based on current conditions (sunny, rainy, stormy, etc.)
- **Smooth Animations** - Fluid 300ms cubic easing animations throughout the interface
- **Animated Sidebar** - Collapsible sidebar with smooth expand/collapse transitions
- **Responsive Design** - Adapts to different window sizes with proper layout management
- **Interactive Elements** - Polished hover effects and visual feedback

### 🌍 **Comprehensive Weather Data**
- **Current Weather** - Real-time data including:
  - Temperature and "feels like" temperature
  - Humidity and atmospheric pressure
  - Wind speed and direction
  - Cloud coverage and visibility
  - Precipitation (rain/snow)
  - Sunrise and sunset times
- **5-Day Forecast** - Detailed daily predictions with weather icons
- **Multiple Locations** - Save unlimited cities and switch between them instantly
- **Auto-Refresh** - Configurable automatic updates (manual, 15min, 30min, 1hr)
- **Location Detection** - Automatic city detection using IP geolocation

### 📰 **Integrated News Feed**
- **Weather News** - Curated weather-related news articles for each location
- **Smart Filtering** - AI-powered filtering to show only relevant weather content
- **Customizable Display** - Choose 5, 10, or 15 articles
- **Time-Aware** - Shows articles from the last 30 days with relative timestamps
- **Direct Links** - One-click access to full articles

### ⚙️ **Extensive Customization**
- **Units Configuration**
  - Temperature: Celsius or Fahrenheit
  - Wind Speed: Metric (m/s) or Imperial (mph)
  - Pressure: Hectopascal (hPa) or Inches of Mercury (inHg)
  - Precipitation: Millimeters (mm) or Inches (in)
- **Display Settings**
  - Time Format: 12-hour or 24-hour
  - Default City: Set preferred startup location
  - Sidebar State: Expanded, collapsed, or remember last state
  - News Count: Customize number of articles
- **Privacy Controls**
  - Enable/disable location services
  - Clear all saved cities
  - No data collection or tracking

### 🎯 **Technical Highlights**
- **Cross-Platform** - Optimized for both macOS and Windows
- **Platform-Specific Configs** - Automatic window sizing and positioning per OS
- **Persistent Storage** - All settings and cities saved locally as JSON
- **Threaded API Calls** - Non-blocking background data fetching
- **Error Handling** - Graceful handling of network issues and API errors
- **OpenWeatherMap Integration** - Reliable weather data from trusted source

---

## 🚀 Installation

### Prerequisites

- **Python 3.7 or higher**
- **pip** (Python package manager)

### Step 1: Clone the Repository

```bash
git clone https://github.com/TRX-1000/Weatherly-v2.git
cd Weatherly-v2
```

### Step 2: Create a Virtual Environment (Recommended)

**Why use a virtual environment?**
- ✅ **Isolates dependencies** - Keeps Weatherly's packages separate from your system Python
- ✅ **Prevents conflicts** - Avoids version clashes with other Python projects
- ✅ **Easy cleanup** - Simply delete the folder to remove everything
- ✅ **Reproducible setup** - Ensures consistent behavior across different machines
- ✅ **Best practice** - Standard in Python development

**Create and activate virtual environment:**

#### On macOS/Linux:
```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# You should see (venv) in your terminal prompt
```

#### On Windows:
```bash
# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate

# You should see (venv) in your terminal prompt
```

> **Note:** To deactivate later, simply run `deactivate`

### Step 3: Install Dependencies

With your virtual environment activated:

```bash
pip install -r requirements.txt
```

**Required packages:**
- `PyQt5` - GUI framework
- `requests` - HTTP requests for weather API
- `feedparser` - RSS feed parsing for news
- `geocoder` - IP-based location detection

### Step 4: Run the Application

```bash
python main.py
```

### Quick Start (All-in-One)

```bash
# Clone and setup
git clone https://github.com/TRX-1000/Weatherly-v2.git
cd Weatherly-v2

# Create virtual environment
python3 -m venv venv  # On Windows: python -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app
python main.py
```

---

## 🎯 Usage

### Getting Started

1. **Launch the app** - Run `python main.py`
2. **Search for a city** - Type a city name in the search bar and press Enter
3. **Add locations** - Cities are automatically saved to the sidebar
4. **Switch cities** - Click any city card in the sidebar to view its weather
5. **Customize settings** - Click the ⚙️ gear icon to open preferences

### Key Controls

| Action | Method |
|--------|--------|
| **Toggle Sidebar** | Click the ☰ menu button |
| **Search Location** | Type in search bar and press Enter |
| **Refresh Weather** | Click the ↻ refresh button |
| **Detect Location** | Click the 📍 location button |
| **Open Settings** | Click the ⚙️ settings button |
| **Delete City** | Right-click city card → Delete |
| **View Forecast** | Scroll down to see 5-day forecast |
| **Read News** | Click any news card to open article |

### Sidebar Management

- **Left-click** a city card to load its weather
- **Right-click** a city card to delete it
- **Triple-click** a city card for a surprise! 🎉

---

## 📸 Screenshots

https://github.com/user-attachments/assets/230c5400-86f1-4b91-864b-8ccabe8e1672
https://github.com/user-attachments/assets/eb72c6d0-c7dc-4605-ba58-d642fbc00251
https://github.com/user-attachments/assets/9f6d4aa6-a508-4f67-ba12-3330fedd9b1a
https://github.com/user-attachments/assets/f90cdb49-11b4-476d-945b-12c30524f007
https://github.com/user-attachments/assets/04175f60-3a86-4f7c-853f-b9f05e99aeab
https://github.com/user-attachments/assets/91e2f03a-67b4-4949-acf4-f89131e44898
https://github.com/user-attachments/assets/e47c527c-ee4d-4472-9572-804fc534729f
---

## ⚙️ Configuration

### Settings File (`settings.json`)

The app stores your preferences in `settings.json`:

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

### Window Configuration (`window_config.json`)

Platform-specific window settings:

```json
{
  "Darwin": {
    "width": 1470,
    "height": 810,
    "min_width": 1470,
    "min_height": 810,
    "start_x": 0,
    "start_y": 0
  },
  "Windows": {
    "width": 1350,
    "height": 775,
    "min_width": 1375,
    "min_height": 775,
    "start_x": 100,
    "start_y": 100
  }
}
```

### API Configuration

The app uses OpenWeatherMap API. To use your own API key:

1. Open `main_window.py`
2. Find line 151: `self.weather_api = WeatherAPI("YOUR_API_KEY")`
3. Replace with your API key from [OpenWeatherMap](https://openweathermap.org/api)

---

## 🎉 Easter Eggs

Weatherly includes several hidden features for users to discover:

1. **🎮 Konami Code** - Enter the classic cheat code for a surprise
2. **🤣 Dad Jokes** - Triple-click any city card for weather-related humor
3. **🔧 Developer Console** - Search for `dev.weather.debug.mode.enable` to access system info
4. **📺 Channel 42** - Search for `channel 42` to enter an alternate dimension
5. **😤 Refresh Spam** - Click refresh 15+ times to see what happens
6. **💬 Search Bar Sass** - Click the empty search bar repeatedly
7. **More to discover...** - Keep exploring!

---

## 🛠️ Project Structure

```
Weatherly-v2/
├── main.py                  # Application entry point
├── requirements.txt         # Python dependencies
├── README.md               # This file
├── .gitignore             # Git ignore rules
│
├── ui/                    # User interface components
│   ├── main_window.py     # Main application window
│   ├── sidebar_card.py    # City weather cards
│   ├── news_card.py       # News article cards
│   └── settings_page.py   # Settings interface
│
├── tools/                 # Backend utilities
│   ├── weather_api.py     # OpenWeatherMap integration
│   ├── news_api.py        # Google News RSS parser
│   ├── location_detector.py  # IP geolocation
│   └── window_config.py   # Platform-specific configs
│
├── assets/               # Media resources
│   ├── background/       # Weather background images
│   │   ├── sunny.jpg
│   │   ├── rain.jpg
│   │   ├── thunderstorm.jpg
│   │   └── ...
│   └── icons/           # Weather condition icons
│       ├── sun.png
│       ├── cloud.png
│       └── ...
│
└── Data files (generated at runtime)
    ├── settings.json        # User preferences
    ├── saved_cities.json    # Saved locations
    └── window_config.json   # Window settings
```

---

## 🔧 Technical Details

### Architecture

- **Frontend**: PyQt5 with custom styled widgets
- **Backend**: Threaded API calls using `QThread` for non-blocking operations
- **Data Storage**: JSON-based local storage
- **API Integration**: OpenWeatherMap API v2.5
- **News Source**: Google News RSS feeds

### Key Components

1. **MainWindow** - Core application controller
   - Manages UI state and layout
   - Handles user interactions
   - Coordinates data fetching

2. **Weather API** - Data retrieval layer
   - Current weather data
   - 5-day/3-hour forecasts
   - Daily summaries with averages

3. **News API** - Content aggregation
   - RSS feed parsing
   - Smart filtering for weather relevance
   - HTML sanitization

4. **Worker Threads** - Background processing
   - `WeatherWorker` - Fetches weather data
   - `NewsWorker` - Fetches news articles
   - `LocationWorker` - Detects user location

### Animation System

Uses `QPropertyAnimation` with `QEasingCurve.OutCubic` for smooth transitions:
- Sidebar expand/collapse
- Button hover effects
- Dynamic content loading

---

## 🎨 Customization Guide

### Adding Weather Backgrounds

1. Add your image to `assets/background/`
2. Update `update_background()` in `main_window.py`:

```python
elif weather_id == YOUR_CONDITION_ID:
    image_name = 'your_image.jpg'
```

### Adding Weather Icons

1. Add icon PNG to `assets/icons/`
2. Update `get_weather_icon_path()` in `main_window.py`:

```python
elif 'your_condition' in desc_lower:
    return 'assets/icons/your_icon.png'
```

### Modifying Colors

Edit the stylesheet values in the widget definitions:

```python
# Sidebar background
background-color: #1a1a1a;

# Main content area
background-color: #111;

# Interactive elements
background: #262626;

# Hover states
background: #333;

# Accent color
color: #4a8fff;
```

---

## 🗺️ Roadmap

### Planned Features

- [ ] **Hourly Forecast** - Hour-by-hour weather predictions
- [ ] **Weather Alerts** - Push notifications for severe weather
- [ ] **Weather Radar** - Interactive precipitation maps
- [ ] **Historical Data** - View past weather trends
- [ ] **Multiple Themes** - Light mode and custom color schemes
- [ ] **Weather Widgets** - Customizable dashboard widgets
- [ ] **Export Data** - Save weather data as CSV/JSON
- [ ] **System Tray Integration** - Quick access from taskbar
- [ ] **Offline Mode** - Cached data when internet unavailable
- [ ] **Weather Comparison** - Side-by-side city comparisons
- [ ] **Air Quality Index** - AQI data integration
- [ ] **UV Index** - Sun exposure information
- [ ] **Weather Graphs** - Visual temperature/precipitation trends

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

### Reporting Bugs

1. Check if the issue already exists
2. Create a detailed bug report including:
   - Steps to reproduce
   - Expected vs actual behavior
   - Screenshots if applicable
   - Your OS and Python version

### Suggesting Features

1. Open an issue with the `enhancement` label
2. Describe the feature and its benefits
3. Include mockups or examples if possible

### Submitting Pull Requests

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/AmazingFeature`)
3. **Commit** your changes (`git commit -m 'Add some AmazingFeature'`)
4. **Push** to the branch (`git push origin feature/AmazingFeature`)
5. **Open** a Pull Request

### Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/Weatherly-v2.git

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app
python main.py
```

### Code Style

- Follow PEP 8 guidelines
- Use meaningful variable names
- Add docstrings to functions
- Comment complex logic
- Keep functions focused and modular

---

## 📝 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2024 Weatherly

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 🙏 Acknowledgments

- **OpenWeatherMap** - Weather data API
- **Google News** - News RSS feeds
- **PyQt5** - GUI framework and community
- **Material Design** - Animation and design inspiration
- **Contributors** - Everyone who has helped improve Weatherly

---

## 📧 Contact & Support

- **GitHub**: [@TRX-1000](https://github.com/TRX-1000)
- **Project Link**: [https://github.com/TRX-1000/Weatherly-v2](https://github.com/TRX-1000/Weatherly-v2)
- **Issues**: [Report a bug or request a feature](https://github.com/TRX-1000/Weatherly-v2/issues)

---

## 💡 FAQ

**Q: Do I need an API key?**  
A: The app comes with a default API key, but for extended use, get your own free key from [OpenWeatherMap](https://openweathermap.org/api).

**Q: Does Weatherly collect my data?**  
A: No. All data is stored locally on your device. No telemetry or tracking.

**Q: Why isn't my city showing up?**  
A: Make sure you're spelling it correctly. Try including the country (e.g., "London, UK").

**Q: Can I change the background images?**  
A: Yes! Add your images to `assets/background/` and update the code. See [Customization Guide](#-customization-guide).

**Q: The app won't start. What should I do?**  
A: Ensure all dependencies are installed (`pip install -r requirements.txt`) and you're using Python 3.7+.

**Q: How do I update Weatherly?**  
A: Pull the latest changes: `git pull origin main` then restart the app.

---

<div align="center">

### ⭐ Star this repository if you find it helpful!

**Made with ❤️ and Python**

[Report Bug](https://github.com/TRX-1000/Weatherly-v2/issues) • [Request Feature](https://github.com/TRX-1000/Weatherly-v2/issues) • [View Demo](#)

---

**Weatherly v2.0** - *Because you deserve beautiful weather forecasts*

</div>
