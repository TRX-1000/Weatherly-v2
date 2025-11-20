from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
    QFrame, QLineEdit, QLabel, QScrollArea
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap
import requests
from io import BytesIO

from ui.sidebar_card import WeatherCard
from tools.weather_api import WeatherAPI


class WeatherWorker(QThread):
    """Background thread for fetching weather data"""
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, weather_api, city, fetch_type="current"):
        super().__init__()
        self.weather_api = weather_api
        self.city = city
        self.fetch_type = fetch_type
    
    def run(self):
        try:
            if self.fetch_type == "current":
                data = self.weather_api.get_current_weather(self.city)
            elif self.fetch_type == "forecast":
                data = self.weather_api.get_daily_summary(self.city)
            
            if data:
                self.finished.emit(data)
            else:
                self.error.emit(f"Could not fetch weather for {self.city}")
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Weatherly")
        self.setMinimumSize(1200, 700)

        # Initialize Weather API (replace with your actual API key)
        self.weather_api = WeatherAPI("69ff8ccadbda20220e57e69ffad4a882")
        self.current_city = None
        self.saved_cities = ["London", "Tokyo", "New York"]  # Default cities
        self.city_cards = {}  # Track cards for updates

        self.sidebar_collapsed = 0
        self.sidebar_expanded = 260
        self.current_sidebar_width = self.sidebar_collapsed

        self.root = QHBoxLayout(self)
        self.root.setContentsMargins(0, 0, 0, 0)
        self.root.setSpacing(0)

        # ---------------- SIDEBAR ----------------
        self.sidebar = QFrame()
        self.sidebar.setStyleSheet("background-color: #1a1a1a;")
        self.sidebar.setFixedWidth(self.sidebar_collapsed)

        sidebar_scroll = QScrollArea()
        sidebar_scroll.setWidgetResizable(True)
        sidebar_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background: #1a1a1a;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #333;
                border-radius: 4px;
            }
        """)

        sidebar_content = QWidget()
        self.sidebar_layout = QVBoxLayout(sidebar_content)
        self.sidebar_layout.setContentsMargins(12, 12, 12, 12)
        self.sidebar_layout.setSpacing(12)

        # Load saved city cards
        self.load_saved_cities()
        self.sidebar_layout.addStretch()

        sidebar_scroll.setWidget(sidebar_content)
        
        sidebar_main_layout = QVBoxLayout(self.sidebar)
        sidebar_main_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_main_layout.addWidget(sidebar_scroll)

        # ---------------- RIGHT PANEL ----------------
        self.right = QFrame()
        self.right.setStyleSheet("background-color: #111;")

        right_layout = QVBoxLayout(self.right)
        right_layout.setContentsMargins(20, 20, 20, 20)
        right_layout.setSpacing(15)

        # Top Bar
        top_bar = QHBoxLayout()
        top_bar.setSpacing(12)

        self.menu_button = QPushButton("☰")
        self.menu_button.setFixedSize(45, 45)
        self.menu_button.setStyleSheet("""
            QPushButton {
                font-size: 22px; 
                border: none; 
                border-radius: 10px;
                background: #262626; 
                color: white;
            }
            QPushButton:hover { background: #333; }
        """)
        self.menu_button.clicked.connect(self.toggle_sidebar)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("🔎 Search for a place... (e.g., 'London' or 'Paris,FR')")
        self.search_bar.setFixedHeight(45)
        self.search_bar.setStyleSheet("""
            QLineEdit {
                background: #262626;
                border-radius: 22px;
                padding-left: 20px;
                color: white;
                font-size: 16px;
            }
            QLineEdit::placeholder {
                color: #777;
            }
        """)
        self.search_bar.returnPressed.connect(self.search_weather)

        self.refresh_button = QPushButton("↻")
        self.refresh_button.setFixedSize(45, 45)
        self.refresh_button.setStyleSheet("""
            QPushButton {
                background: #262626;
                border-radius: 10px;
                color: white;
                font-size: 24px;
            }
            QPushButton:hover { background: #333; }
        """)
        self.refresh_button.clicked.connect(self.refresh_weather)

        top_bar.addWidget(self.menu_button)
        top_bar.addWidget(self.search_bar)
        top_bar.addWidget(self.refresh_button)

        right_layout.addLayout(top_bar)

        # Main Content Area
        self.content = QFrame()
        self.content.setStyleSheet("background: #181818; border-radius: 14px;")
        
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(30, 30, 30, 30)
        self.content_layout.setSpacing(20)

        # Current weather display
        self.create_current_weather_section()
        
        # 5-day forecast display
        self.create_forecast_section()

        right_layout.addWidget(self.content)

        # Add sidebar + main
        self.root.addWidget(self.sidebar)
        self.root.addWidget(self.right)

        # Animations
        self.sidebar_anim = QPropertyAnimation(self.sidebar, b"minimumWidth")
        self.sidebar_anim.setDuration(300)
        self.sidebar_anim.setEasingCurve(QEasingCurve.InOutCubic)

        self.search_anim = QPropertyAnimation(self.search_bar, b"maximumWidth")
        self.search_anim.setDuration(300)
        self.search_anim.setEasingCurve(QEasingCurve.InOutCubic)

        # Load default city
        self.search_bar.setText("London")
        self.search_weather()

    # ---------------- UI Sections ----------------
    def create_current_weather_section(self):
        """Create the current weather display section"""
        self.current_section = QFrame()
        self.current_section.setStyleSheet("""
            QFrame {
                background: #262626;
                border-radius: 14px;
            }
        """)
        
        current_layout = QVBoxLayout(self.current_section)
        current_layout.setContentsMargins(25, 25, 25, 25)
        current_layout.setSpacing(15)

        # City name
        self.city_label = QLabel("Select a city to view weather")
        self.city_label.setStyleSheet("font-size: 32px; font-weight: bold; color: white;")
        
        # Temperature
        self.temp_label = QLabel("--°C")
        self.temp_label.setStyleSheet("font-size: 72px; font-weight: bold; color: white;")
        
        # Description
        self.description_label = QLabel("--")
        self.description_label.setStyleSheet("font-size: 20px; color: #ccc;")
        
        # Details grid
        details_layout = QHBoxLayout()
        details_layout.setSpacing(30)
        
        self.feels_like_label = QLabel("Feels like: --°C")
        self.feels_like_label.setStyleSheet("font-size: 16px; color: #aaa;")
        
        self.humidity_label = QLabel("Humidity: --%")
        self.humidity_label.setStyleSheet("font-size: 16px; color: #aaa;")
        
        self.wind_label = QLabel("Wind: -- m/s")
        self.wind_label.setStyleSheet("font-size: 16px; color: #aaa;")
        
        details_layout.addWidget(self.feels_like_label)
        details_layout.addWidget(self.humidity_label)
        details_layout.addWidget(self.wind_label)
        details_layout.addStretch()
        
        current_layout.addWidget(self.city_label)
        current_layout.addWidget(self.temp_label)
        current_layout.addWidget(self.description_label)
        current_layout.addLayout(details_layout)
        
        self.content_layout.addWidget(self.current_section)

    def create_forecast_section(self):
        """Create the 5-day forecast section"""
        forecast_header = QLabel("5-Day Forecast")
        forecast_header.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")
        self.content_layout.addWidget(forecast_header)
        
        self.forecast_container = QFrame()
        self.forecast_container.setStyleSheet("background: transparent;")
        
        self.forecast_layout = QHBoxLayout(self.forecast_container)
        self.forecast_layout.setSpacing(15)
        self.forecast_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create 5 forecast cards
        self.forecast_cards = []
        for i in range(5):
            card = self.create_forecast_card()
            self.forecast_cards.append(card)
            self.forecast_layout.addWidget(card)
        
        self.content_layout.addWidget(self.forecast_container)
        self.content_layout.addStretch()

    def create_forecast_card(self):
        """Create a single forecast day card"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: #262626;
                border-radius: 12px;
            }
        """)
        card.setFixedSize(180, 200)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignCenter)
        
        day_label = QLabel("--")
        day_label.setStyleSheet("font-size: 18px; font-weight: bold; color: white;")
        day_label.setAlignment(Qt.AlignCenter)
        
        icon_label = QLabel("🌤️")
        icon_label.setStyleSheet("font-size: 48px;")
        icon_label.setAlignment(Qt.AlignCenter)
        
        temp_label = QLabel("--°")
        temp_label.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")
        temp_label.setAlignment(Qt.AlignCenter)
        
        desc_label = QLabel("--")
        desc_label.setStyleSheet("font-size: 14px; color: #aaa;")
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        
        layout.addWidget(day_label)
        layout.addWidget(icon_label)
        layout.addWidget(temp_label)
        layout.addWidget(desc_label)
        
        # Store references for updating
        card.day_label = day_label
        card.icon_label = icon_label
        card.temp_label = temp_label
        card.desc_label = desc_label
        
        return card

    # ---------------- Weather Data Fetching ----------------
    def load_saved_cities(self):
        """Load weather cards for saved cities"""
        for city in self.saved_cities:
            card = WeatherCard(city)
            card.mousePressEvent = lambda event, c=city: self.load_city_weather(c)
            card.setCursor(Qt.PointingHandCursor)
            self.city_cards[city] = card
            self.sidebar_layout.addWidget(card)
            
            # Fetch weather for this city
            self.fetch_city_weather(city)

    def fetch_city_weather(self, city):
        """Fetch weather for a sidebar city card"""
        worker = WeatherWorker(self.weather_api, city, "current")
        worker.finished.connect(lambda data: self.update_city_card(city, data))
        worker.error.connect(lambda err: print(f"Error loading {city}: {err}"))
        worker.start()
        # Keep reference to prevent garbage collection
        if not hasattr(self, 'workers'):
            self.workers = []
        self.workers.append(worker)

    def update_city_card(self, city, data):
        """Update a sidebar city card with fetched data"""
        if city in self.city_cards:
            card = self.city_cards[city]
            temp = f"{int(data['temperature'])}°"
            condition = data['description'].title()
            hi = f"{int(data['temp_max'])}°"
            lo = f"{int(data['temp_min'])}°"
            card.update_weather(temp, condition, hi, lo)

    def load_city_weather(self, city):
        """Load weather for a city when its card is clicked"""
        self.search_bar.setText(city)
        self.search_weather()

    def search_weather(self):
        """Search and display weather for the city in search bar"""
        city = self.search_bar.text().strip()
        if not city:
            return
        
        self.current_city = city
        
        # Fetch current weather
        current_worker = WeatherWorker(self.weather_api, city, "current")
        current_worker.finished.connect(self.update_current_weather)
        current_worker.error.connect(self.show_error)
        current_worker.start()
        
        # Fetch forecast
        forecast_worker = WeatherWorker(self.weather_api, city, "forecast")
        forecast_worker.finished.connect(self.update_forecast)
        forecast_worker.error.connect(self.show_error)
        forecast_worker.start()
        
        # Keep references
        if not hasattr(self, 'workers'):
            self.workers = []
        self.workers.extend([current_worker, forecast_worker])

    def update_current_weather(self, data):
        """Update current weather display"""
        self.city_label.setText(f"{data['city']}, {data['country']}")
        self.temp_label.setText(f"{int(data['temperature'])}°C")
        self.description_label.setText(data['description'].title())
        self.feels_like_label.setText(f"Feels like: {int(data['feels_like'])}°C")
        self.humidity_label.setText(f"Humidity: {data['humidity']}%")
        self.wind_label.setText(f"Wind: {data['wind_speed']:.1f} m/s")

    def update_forecast(self, data):
        """Update 5-day forecast display"""
        daily = data['daily'][:5]  # Get first 5 days
        
        for i, day_data in enumerate(daily):
            if i < len(self.forecast_cards):
                card = self.forecast_cards[i]
                
                # Update day name
                card.day_label.setText(day_data['day_name'][:3])  # Mon, Tue, etc.
                
                # Update temperature
                avg_temp = int(day_data['temp_avg'])
                card.temp_label.setText(f"{avg_temp}°C")
                
                # Update description
                card.desc_label.setText(day_data['description'].title())
                
                # Map weather icons
                icon = self.get_weather_emoji(day_data['description'])
                card.icon_label.setText(icon)

    def get_weather_emoji(self, description):
        """Map weather description to emoji"""
        desc_lower = description.lower()
        if 'clear' in desc_lower:
            return '☀️'
        elif 'cloud' in desc_lower:
            return '☁️'
        elif 'rain' in desc_lower or 'drizzle' in desc_lower:
            return '🌧️'
        elif 'thunder' in desc_lower or 'storm' in desc_lower:
            return '⛈️'
        elif 'snow' in desc_lower:
            return '❄️'
        elif 'mist' in desc_lower or 'fog' in desc_lower:
            return '🌫️'
        else:
            return '🌤️'

    def show_error(self, error_msg):
        """Display error message"""
        self.city_label.setText("Error")
        self.temp_label.setText("--°C")
        self.description_label.setText(error_msg)
        print(f"Error: {error_msg}")

    def refresh_weather(self):
        """Refresh current weather"""
        if self.current_city:
            self.search_weather()
        
        # Also refresh sidebar cities
        for city in self.saved_cities:
            self.fetch_city_weather(city)

    # ---------------- Sidebar Animation ----------------
    def toggle_sidebar(self):
        if self.current_sidebar_width == self.sidebar_collapsed:
            self.expand_sidebar()
        else:
            self.collapse_sidebar()

    def expand_sidebar(self):
        self.current_sidebar_width = self.sidebar_expanded
        diff = self.sidebar_expanded - self.sidebar_collapsed

        self.sidebar_anim.setStartValue(self.sidebar.width())
        self.sidebar_anim.setEndValue(self.sidebar_expanded)
        self.sidebar_anim.start()

        self.search_anim.setStartValue(self.search_bar.width())
        self.search_anim.setEndValue(max(150, self.search_bar.width() - diff))
        self.search_anim.start()

    def collapse_sidebar(self):
        self.current_sidebar_width = self.sidebar_collapsed
        diff = self.sidebar_expanded - self.sidebar_collapsed

        self.sidebar_anim.setStartValue(self.sidebar.width())
        self.sidebar_anim.setEndValue(self.sidebar_collapsed)
        self.sidebar_anim.start()

        self.search_anim.setStartValue(self.search_bar.width())
        self.search_anim.setEndValue(self.search_bar.width() + diff)
        self.search_anim.start()