import json
import os
from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
    QFrame, QLineEdit, QLabel, QScrollArea, QMenu, QAction, QGraphicsBlurEffect
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QThread, pyqtSignal
from PyQt5.QtGui import QCursor, QPixmap

from ui.sidebar_card import WeatherCard
from ui.news_card import NewsCard
from ui.settings_page import SettingsPage

from tools.weather_api import WeatherAPI
from tools.news_api import NewsAPI
from tools.window_config import WindowConfig


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

        self.window_config = WindowConfig("window_config.json")

        self.setWindowTitle("Weatherly")

        # Apply platform-specific window settings
        width = self.window_config.get_width()
        height = self.window_config.get_height()
        min_width = self.window_config.get_min_width()
        min_height = self.window_config.get_min_height()

        self.setGeometry(100, 100, width, height)
        self.setMinimumSize(min_width, min_height)

        

        # Initialize APIs
        self.weather_api = WeatherAPI("69ff8ccadbda20220e57e69ffad4a882")
        self.news_api = NewsAPI()
        self.current_city = None
        self.saved_cities = []
        self.city_cards = {}
        self.news_workers = []
        
        # Load saved cities from file
        self.cities_file = "saved_cities.json"
        self.load_cities_from_file()

        # Load settings from file
        self.settings_file = "settings.json"
        self.settings = self.load_settings()

    
        self.sidebar_collapsed = 0
        self.sidebar_expanded = 280
        self.current_sidebar_width = self.sidebar_expanded  # Start expanded

        self.root = QHBoxLayout(self)
        self.root.setContentsMargins(0, 0, 0, 0)
        self.root.setSpacing(0)

        # ---------------- SIDEBAR ----------------
        self.sidebar = QFrame()
        self.sidebar.setStyleSheet("background-color: #1a1a1a;")
        self.sidebar.setMinimumWidth(self.sidebar_expanded)
        self.sidebar.setMaximumWidth(self.sidebar_expanded)

        sidebar_main_layout = QVBoxLayout(self.sidebar)
        sidebar_main_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_main_layout.setSpacing(0)

        # Sidebar header with menu button
        sidebar_header = QFrame()
        sidebar_header.setStyleSheet("background-color: #1a1a1a;")
        header_layout = QHBoxLayout(sidebar_header)
        header_layout.setContentsMargins(15, 15, 15, 10)
        header_layout.setSpacing(10)

        self.menu_button = QPushButton("☰")
        self.menu_button.setFixedSize(40, 40)
        self.menu_button.setStyleSheet("""
            QPushButton {
                font-size: 20px; 
                border: none; 
                border-radius: 8px;
                background: #262626; 
                color: white;
            }
            QPushButton:hover { background: #333; }
        """)
        self.menu_button.clicked.connect(self.toggle_sidebar)

        sidebar_title = QLabel("Weatherly")
        sidebar_title.setStyleSheet("font-size: 20px; font-weight: bold; color: white;")

        header_layout.addWidget(self.menu_button)
        header_layout.addWidget(sidebar_title)
        header_layout.addStretch()

        # Search bar in sidebar
        search_container = QFrame()
        search_container.setStyleSheet("background-color: #1a1a1a;")
        search_layout = QVBoxLayout(search_container)
        search_layout.setContentsMargins(15, 5, 15, 15)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("🔎 Search location...")
        self.search_bar.setFixedHeight(40)
        self.search_bar.setStyleSheet("""
            QLineEdit {
                background: #262626;
                border-radius: 20px;
                padding-left: 15px;
                padding-right: 15px;
                color: white;
                font-size: 14px;
                border: 1px solid #333;
            }
            QLineEdit::placeholder {
                color: #777;
            }
            QLineEdit:focus {
                border: 1px solid #444;
            }
        """)
        self.search_bar.returnPressed.connect(self.search_weather)

        search_layout.addWidget(self.search_bar)

        # Scrollable cities list
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
        self.sidebar_layout.setContentsMargins(12, 5, 12, 12)
        self.sidebar_layout.setSpacing(12)

        self.load_saved_cities()
        self.sidebar_layout.addStretch()

        sidebar_scroll.setWidget(sidebar_content)
        
        sidebar_main_layout.addWidget(sidebar_header)
        sidebar_main_layout.addWidget(search_container)
        sidebar_main_layout.addWidget(sidebar_scroll)

        # ---------------- RIGHT PANEL ----------------
        self.right = QFrame()
        self.right.setStyleSheet("background-color: #111;")
        
        # Background label for weather images
        self.background_label = QLabel(self.right)
        self.background_label.setScaledContents(False)
        self.background_label.setAlignment(Qt.AlignCenter)
        self.background_label.lower()  # Send to back
        
        # Add blur effect to background
        self.blur_effect = QGraphicsBlurEffect()
        self.blur_effect.setBlurRadius(15)  # Adjust blur intensity
        self.background_label.setGraphicsEffect(self.blur_effect)
        
        # Dimming overlay on top of background
        self.dim_overlay = QLabel(self.right)
        self.dim_overlay.setStyleSheet("background-color: rgba(0, 0, 0, 0.3);")  # 30% black overlay
        self.dim_overlay.setGeometry(0, 0, 1920, 1080)  # Set initial large size
        self.dim_overlay.lower()  # Above background but below content

        right_layout = QVBoxLayout(self.right)
        right_layout.setContentsMargins(20, 20, 20, 20)
        right_layout.setSpacing(15)
        
        # Raise the layout widget to be on top of the dim overlay
        if hasattr(self, 'dim_overlay'):
            self.dim_overlay.lower()
            self.background_label.lower()

        # Top Bar - Container for centering
        top_bar_container = QHBoxLayout()
        top_bar_container.setContentsMargins(0, 0, 0, 0)
        top_bar_container.setSpacing(0)

        # Left side - Menu button (when collapsed)
        self.floating_menu_button = QPushButton("☰")
        self.floating_menu_button.setFixedSize(45, 45)
        self.floating_menu_button.setStyleSheet("""
            QPushButton {
                font-size: 22px; 
                border: none; 
                border-radius: 10px;
                background: #262626; 
                color: white;
            }
            QPushButton:hover { background: #333; }
        """)
        self.floating_menu_button.clicked.connect(self.toggle_sidebar)
        self.floating_menu_button.hide()

        # Center spacer (pushes content to center)
        center_spacer = QWidget()
        center_spacer.setSizePolicy(center_spacer.sizePolicy().Expanding, center_spacer.sizePolicy().Fixed)

        # Right side - Refresh button
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

        self.settings_button = QPushButton("⚙️")
        self.settings_button.setFixedSize(45, 45)
        self.settings_button.setStyleSheet("""
            QPushButton {
                background: #262626;
                border-radius: 10px;
                color: white;
                font-size: 22px;
            }
            QPushButton:hover { background: #333; }""")
        
        self.settings_button.clicked.connect(self.open_settings)


        top_bar_container.addWidget(self.floating_menu_button)
        top_bar_container.addWidget(center_spacer)
        top_bar_container.addWidget(self.settings_button)
        top_bar_container.addWidget(self.refresh_button)

        right_layout.addLayout(top_bar_container)

        # Main Content Area with Scroll
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: #111;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #333;
                border-radius: 5px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background: #444;
            }
        """)

        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        
        self.content_layout = QVBoxLayout(scroll_content)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(20)

        # Current weather display
        self.create_current_weather_section()
        
        # 5-day forecast display
        self.create_forecast_section()
        
        # News section
        self.create_news_section()

        self.content_layout.addStretch()

        self.scroll_area.setWidget(scroll_content)
        right_layout.addWidget(self.scroll_area)

        # Add sidebar + main
        self.root.addWidget(self.sidebar)
        self.root.addWidget(self.right)

        # Create settings page overlay (covers entire window including sidebar)
        self.settings_page = SettingsPage(self, self.settings)
        self.settings_page.settings_changed.connect(self.apply_settings)
        self.settings_page.back_clicked.connect(self.show_weather_content)
        self.settings_page.hide()
        self.settings_page.setGeometry(0, 0, self.width(), self.height())
        self.settings_page.raise_()
        
        # Ensure proper z-ordering: background at bottom, dim overlay above it, content on top
        if hasattr(self, 'background_label'):
            self.background_label.lower()
        if hasattr(self, 'dim_overlay'):
            self.dim_overlay.lower()
            self.dim_overlay.raise_()  # Raise above background
            self.background_label.lower()  # But keep background at very bottom

        self.floating_menu_button.raise_()
        self.settings_button.raise_()
        self.refresh_button.raise_()
        self.scroll_area.raise_()

        # Animations
        self.sidebar_anim = QPropertyAnimation(self.sidebar, b"minimumWidth")
        self.sidebar_anim.setDuration(250)
        self.sidebar_anim.setEasingCurve(QEasingCurve.OutCubic)
        self.sidebar_anim.valueChanged.connect(self.update_background_geometry)
        
        self.sidebar_max_anim = QPropertyAnimation(self.sidebar, b"maximumWidth")
        self.sidebar_max_anim.setDuration(250)
        self.sidebar_max_anim.setEasingCurve(QEasingCurve.OutCubic)

        # Load default city if available
        if self.saved_cities:
            self.search_bar.setText(self.saved_cities[0])
            self.search_weather()

    # ---------------- City Persistence ----------------
    def load_cities_from_file(self):
        """Load saved cities from JSON file"""
        if os.path.exists(self.cities_file):
            try:
                with open(self.cities_file, 'r') as f:
                    self.saved_cities = json.load(f)
            except Exception as e:
                print(f"Error loading cities: {e}")
                self.saved_cities = ["London", "Tokyo", "New York"]
        else:
            # Default cities if no file exists
            self.saved_cities = ["London", "Tokyo", "New York"]
    
    def save_cities_to_file(self):
        """Save cities to JSON file"""
        try:
            with open(self.cities_file, 'w') as f:
                json.dump(self.saved_cities, f, indent=2)
        except Exception as e:
            print(f"Error saving cities: {e}")

    # ---------------- UI Sections ----------------
    def create_current_weather_section(self):
        """Create the current weather display section"""
        self.current_section = QFrame()
        self.current_section.setStyleSheet("""
            QFrame {
                background: none;
                border-radius: 20px;
            }
        """)
        
        current_layout = QVBoxLayout(self.current_section)
        current_layout.setContentsMargins(35, 35, 35, 35)
        current_layout.setSpacing(15)

        self.city_label = QLabel("Select a city to view weather")
        self.city_label.setStyleSheet("font-size: 34px; font-weight: bold; color: white; background: none;")
        
        self.temp_label = QLabel("--°C")
        self.temp_label.setStyleSheet("font-size: 82px; font-weight: bold; color: white; background: none;")
        
        self.description_label = QLabel("--")
        self.description_label.setStyleSheet("font-size: 22px; color: #fff; background: none;")
        
        details_layout = QHBoxLayout()
        details_layout.setSpacing(40)
        
        self.feels_like_label = QLabel("Feels like: --°C")
        self.feels_like_label.setStyleSheet("font-size: 17px; color: #ffffff; background: none;")
        
        self.humidity_label = QLabel("Humidity: --%")
        self.humidity_label.setStyleSheet("font-size: 17px; color: #ffffff; background: none;")
        
        self.wind_label = QLabel("Wind: -- m/s")
        self.wind_label.setStyleSheet("font-size: 17px; color: #ffffff; background: none;")
        
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
        forecast_header.setStyleSheet("""
            font-size: 26px; 
            font-weight: bold; 
            color: white;
            padding-left: 5px;
        """)
        self.content_layout.addWidget(forecast_header)
        
        self.forecast_container = QFrame()
        self.forecast_container.setStyleSheet("background: transparent;")
        
        self.forecast_layout = QHBoxLayout(self.forecast_container)
        self.forecast_layout.setSpacing(15)
        self.forecast_layout.setContentsMargins(0, 0, 0, 0)
        
        self.forecast_cards = []
        for i in range(5):
            card = self.create_forecast_card()
            self.forecast_cards.append(card)
            self.forecast_layout.addWidget(card)
        
        self.content_layout.addWidget(self.forecast_container)

    def create_forecast_card(self):
        """Create a single forecast day card"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: none;
                border-radius: 16px;
            }
        """)
        card.setFixedSize(190, 220)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 20, 15, 20)
        layout.setSpacing(12)
        layout.setAlignment(Qt.AlignCenter)
        
        day_label = QLabel("--")
        day_label.setStyleSheet("font-size: 19px; font-weight: bold; color: white; background: none;")
        day_label.setAlignment(Qt.AlignCenter)
        
        icon_label = QLabel("🌤️")
        icon_label.setStyleSheet("font-size: 52px; background: none;")
        icon_label.setAlignment(Qt.AlignCenter)
        
        temp_label = QLabel("--°")
        temp_label.setStyleSheet("font-size: 26px; font-weight: bold; color: white; background: none;")
        temp_label.setAlignment(Qt.AlignCenter)
        
        desc_label = QLabel("--")
        desc_label.setStyleSheet("font-size: 14px; color: #ffffff; background: none;")
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        
        layout.addWidget(day_label)
        layout.addWidget(icon_label)
        layout.addWidget(temp_label)
        layout.addWidget(desc_label)
        
        card.day_label = day_label
        card.icon_label = icon_label
        card.temp_label = temp_label
        card.desc_label = desc_label
        
        return card

    def create_news_section(self):
        """Create the news section"""
        news_header = QLabel("📰 Weather News")
        news_header.setStyleSheet("""
            font-size: 26px; 
            font-weight: bold; 
            background: none;
            color: white;
            padding-left: 5px;
            margin-top: 10px;
        """)
        self.content_layout.addWidget(news_header)
        
        self.news_container = QFrame()
        self.news_container.setStyleSheet("background: transparent;")
        
        self.news_layout = QVBoxLayout(self.news_container)
        self.news_layout.setSpacing(15)
        self.news_layout.setContentsMargins(0, 0, 0, 0)
        
        self.content_layout.addWidget(self.news_container)

    # ---------------- Weather Data Fetching ----------------
    def load_saved_cities(self):
        """Load weather cards for saved cities"""
        for city in self.saved_cities:
            self.create_city_card(city)
    
    def create_city_card(self, city):
        """Create a city card with all event handlers"""
        card = WeatherCard(city)
        card.city_name = city
        
        # Left click handler
        card.mousePressEvent = self.create_card_click_handler(city, card)
        
        # Right click context menu
        card.setContextMenuPolicy(Qt.CustomContextMenu)
        card.customContextMenuRequested.connect(lambda pos, c=city, w=card: self.show_city_context_menu(pos, c, w))
        
        card.setCursor(QCursor(Qt.PointingHandCursor))
        self.city_cards[city] = card
        self.sidebar_layout.addWidget(card)
        
        # Fetch weather for this card
        self.fetch_city_weather(city)
    
    def create_card_click_handler(self, city, card):
        """Create a click handler for a city card"""
        def handler(event):
            # Only handle left clicks
            if event.button() == Qt.LeftButton:
                self.load_city_weather(city)
        return handler
    
    def show_city_context_menu(self, position, city, card):
        """Show context menu for city card"""
        context_menu = QMenu(self)
        context_menu.setStyleSheet("""
            QMenu {
                background-color: #262626;
                color: white;
                border: 1px solid #444;
                border-radius: 8px;
                padding: 5px;
            }
            QMenu::item {
                padding: 8px 20px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #333;
            }
        """)
        
        delete_action = QAction("🗑️ Delete", self)
        delete_action.triggered.connect(lambda: self.delete_city(city, card))
        context_menu.addAction(delete_action)
        
        # Show menu at cursor position
        context_menu.exec_(card.mapToGlobal(position))

    def fetch_city_weather(self, city):
        """Fetch weather for a sidebar city card"""
        try:
            worker = WeatherWorker(self.weather_api, city, "current")
            worker.finished.connect(lambda data, c=city: self.update_city_card(c, data))
            worker.error.connect(lambda err, c=city: self.handle_city_card_error(c, err))
            worker.start()
            if not hasattr(self, 'workers'):
                self.workers = []
            self.workers.append(worker)
        except Exception as e:
            print(f"Error creating worker for {city}: {e}")
    
    def handle_city_card_error(self, city, err):
        """Handle errors when loading city card weather"""
        print(f"Error loading {city}: {err}")
        if city in self.city_cards:
            card = self.city_cards[city]
            card.update_weather("--°", "Error", "--°", "--°")

    def update_city_card(self, city, data):
        """Update a sidebar city card with fetched data"""
        if city in self.city_cards:
            card = self.city_cards[city]
            temp = self.format_temperature(data['temperature'])
            condition = data['description'].title()
            hi = self.format_temperature(data['temp_max'])
            lo = self.format_temperature(data['temp_min'])
            card.update_weather(temp, condition, hi, lo)

    def load_city_weather(self, city):
        """Load weather for a city when its card is clicked"""
        try:
            self.search_bar.setText(city)
            self.search_weather()
        except Exception as e:
            print(f"Error loading city weather: {e}")
            import traceback
            traceback.print_exc()

    def search_weather(self):
        """Search and display weather for the city in search bar"""
        city = self.search_bar.text().strip()
        if not city:
            return
        
        try:
            self.current_city = city
            
            # Add city to sidebar if not already there
            self.add_city_to_sidebar(city)
            
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
            
            # Fetch news
            self.fetch_news(city)
            
            if not hasattr(self, 'workers'):
                self.workers = []
            self.workers.extend([current_worker, forecast_worker])
        except Exception as e:
            print(f"Error in search_weather: {e}")
            import traceback
            traceback.print_exc()
    
    def add_city_to_sidebar(self, city):
        """Add a city to the sidebar if it doesn't exist"""
        # Check if city already exists (case-insensitive)
        city_lower = city.lower()
        for existing_city in self.saved_cities:
            if existing_city.lower() == city_lower:
                return  # City already exists
        
        # Add to saved cities list
        self.saved_cities.append(city)
        self.save_cities_to_file()
        
        # Insert before the stretch at the end
        stretch_item = self.sidebar_layout.takeAt(self.sidebar_layout.count() - 1)
        
        # Create the card
        self.create_city_card(city)
        
        # Add stretch back
        if stretch_item:
            self.sidebar_layout.addItem(stretch_item)
    
    def delete_city(self, city, card):
        """Delete a city from the sidebar"""
        try:
            # Remove from saved cities list
            if city in self.saved_cities:
                self.saved_cities.remove(city)
                self.save_cities_to_file()
            
            # Remove from city cards dict
            if city in self.city_cards:
                del self.city_cards[city]
            
            # Remove the card widget
            self.sidebar_layout.removeWidget(card)
            card.deleteLater()
            
            # If this was the current city, clear the display
            if self.current_city == city:
                self.current_city = None
                self.city_label.setText("Select a city to view weather")
                self.temp_label.setText("--°C")
                self.description_label.setText("--")
                self.clear_news()
        except Exception as e:
            print(f"Error deleting city: {e}")
            import traceback
            traceback.print_exc()

    # ---------------- Settings Management ----------------
    def load_settings(self):
        """Load settings from JSON file"""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading settings: {e}")
        
        # Default settings
        return {
            "temperature_unit": "celsius",
            "wind_unit": "metric",
            "auto_refresh": True
        }

    def save_settings_to_file(self):
        """Save settings to JSON file"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def open_settings(self):
        """Show settings page"""
        self.settings_page.setGeometry(0, 0, self.width(), self.height())
        self.settings_page.show()
        self.settings_page.raise_()

    def show_weather_content(self):
        """Show weather content and hide settings"""
        self.settings_page.hide()

    def apply_settings(self, new_settings):
        """Apply new settings"""
        self.settings = new_settings
        self.save_settings_to_file()
        
        # Refresh weather with new units if a city is loaded
        if self.current_city:
            self.refresh_weather()

    def convert_temperature(self, temp_celsius):
        """Convert temperature based on settings"""
        if self.settings.get("temperature_unit") == "fahrenheit":
            return (temp_celsius * 9/5) + 32
        return temp_celsius

    def format_temperature(self, temp_celsius):
        """Format temperature with correct unit"""
        converted = self.convert_temperature(temp_celsius)
        unit = "°F" if self.settings.get("temperature_unit") == "fahrenheit" else "°C"
        return f"{int(converted)}{unit}"

    def convert_wind_speed(self, speed_ms):
        """Convert wind speed based on settings"""
        if self.settings.get("wind_unit") == "imperial":
            return speed_ms * 2.237  # Convert m/s to mph
        return speed_ms

    def format_wind_speed(self, speed_ms):
        """Format wind speed with correct unit"""
        converted = self.convert_wind_speed(speed_ms)
        unit = "mph" if self.settings.get("wind_unit") == "imperial" else "m/s"
        return f"{converted:.1f} {unit}"

    def fetch_news(self, city):
        """Fetch weather news for the city"""
        # Clear existing news
        self.clear_news()
        
        # Create and show loading indicator
        loading_label = QLabel(f"🔄 Loading news for {city}...")
        loading_label.setStyleSheet("""
            font-size: 15px; 
            color: #888;
            background: none;
            border-radius: 12px;
            padding: 20px;
        """)
        loading_label.setAlignment(Qt.AlignCenter)
        self.news_layout.addWidget(loading_label)
        
        # Fetch news
        worker = self.news_api.get_weather_news(city, self.update_news, self.show_news_error)
        self.news_workers.append(worker)

    def clear_news(self):
        """Clear existing news cards"""
        while self.news_layout.count() > 0:
            item = self.news_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def update_news(self, news_items):
        """Update news display"""
        self.clear_news()
        
        if not news_items:
            no_news_label = QLabel("📭 No recent weather news found for this location.")
            no_news_label.setStyleSheet("""
                font-size: 15px; 
                color: #888;
                background: none;
                border-radius: 12px;
                padding: 25px;
            """)
            no_news_label.setAlignment(Qt.AlignCenter)
            self.news_layout.addWidget(no_news_label)
            return
        
        for item in news_items:
            news_card = NewsCard(
                item["title"],
                item["source"],
                item["published"],
                item["summary"],
                item["link"]
            )

            news_card.setMaximumWidth(755)
            self.news_layout.addWidget(news_card)

    def show_news_error(self, error_msg):
        """Display news error"""
        self.clear_news()
        error_label = QLabel(f"⚠️ Error loading news: {error_msg}")
        error_label.setStyleSheet("""
            font-size: 15px; 
            color: #ff6b6b;
            background: none;
            border-radius: 12px;
            padding: 20px;
        """)
        error_label.setAlignment(Qt.AlignCenter)
        self.news_layout.addWidget(error_label)

    def update_current_weather(self, data):
        """Update current weather display"""
        self.city_label.setText(f"{data['city']}, {data['country']}")
        self.temp_label.setText(self.format_temperature(data['temperature']))
        self.description_label.setText(data['description'].title())
        self.feels_like_label.setText(f"Feels like: {self.format_temperature(data['feels_like'])}")
        self.humidity_label.setText(f"Humidity: {data['humidity']}%")
        self.wind_label.setText(f"Wind: {self.format_wind_speed(data['wind_speed'])}")
        
        # Update background based on weather using weather ID
        weather_id = data.get('id', 800)
        self.update_background(weather_id)
    
    def update_background(self, weather_id):
        """Update background image based on OpenWeatherMap weather ID"""
        # Map OpenWeatherMap weather IDs to background images
        # Reference: https://openweathermap.org/weather-conditions
        
        # Determine which image to use based on weather ID ranges
        if 200 <= weather_id < 300:
            # Thunderstorm (200-232)
            image_name = 'thunderstorm.jpg'
        elif 300 <= weather_id < 400:
            # Drizzle (300-321)
            image_name = 'rain.jpg'
        elif 500 <= weather_id < 505:
            # Light to moderate rain (500-504)
            image_name = 'rain.jpg'
        elif 505 <= weather_id < 600:
            # Heavy rain and extreme rain (505-531)
            image_name = 'heavy_rain.jpg'
        elif 600 <= weather_id < 700:
            # Snow (600-622)
            image_name = 'snow.jpg'
        elif 701 <= weather_id <= 711:
            # Mist, Smoke (701-711)
            image_name = 'fog.jpg'
        elif 721 <= weather_id <= 741:
            # Haze, Fog (721-741)
            image_name = 'fog.jpg'
        elif 751 <= weather_id <= 762:
            # Sand, Dust, Ash (751-762)
            image_name = 'dust.jpg'
        elif weather_id == 771:
            # Squall
            image_name = 'squall.jpg'
        elif weather_id == 781:
            # Tornado
            image_name = 'serious_weather.jpg'
        elif weather_id == 800:
            # Clear sky (800)
            image_name = 'sunny.jpg'
        elif weather_id == 801:
            # Few clouds (801)
            image_name = 'broken_clouds.jpg'
        elif weather_id == 802:
            # Scattered clouds (802)
            image_name = 'broken_clouds.jpg'
        elif weather_id == 803:
            # Broken clouds (803)
            image_name = 'broken_clouds.jpg'
        elif weather_id == 804:
            # Overcast clouds (804)
            image_name = 'overcast.jpg'
        else:
            # Fallback
            image_name = 'sunny.jpg'
        
        image_path = f'assets/background/{image_name}'
        
        # Check if file exists
        if not os.path.exists(image_path):
            # If image doesn't exist, use dark background
            self.right.setStyleSheet("background-color: #111;")
            return
        
        # Load the image
        pixmap = QPixmap(image_path)
        
        if pixmap.isNull():
            # If image failed to load, use dark background
            self.right.setStyleSheet("background-color: #111;")
            return
        
        # Scale pixmap to fit the right panel while maintaining aspect ratio
        scaled_pixmap = pixmap.scaled(
            self.right.size(),
            Qt.KeepAspectRatioByExpanding,
            Qt.SmoothTransformation
        )
        
        # Set the background image
        self.background_label.setPixmap(scaled_pixmap)
        self.background_label.setGeometry(0, 0, self.right.width(), self.right.height())
        
        # Update dim overlay to cover entire right panel
        if hasattr(self, 'dim_overlay'):
            self.dim_overlay.setGeometry(0, 0, self.right.width(), self.right.height())
            self.background_label.stackUnder(self.dim_overlay)  # Background under dim overlay
            
            # Make sure all content widgets are above the overlay
            if hasattr(self, 'scroll_area'):
                self.scroll_area.raise_()
                self.settings_button.raise_()  
                self.refresh_button.raise_() 
                self.floating_menu_button.raise_() 

    def update_background_geometry(self):
        """Update background and overlay geometry during sidebar animation"""
        if hasattr(self, 'background_label') and self.background_label.pixmap():
            scaled_pixmap = self.background_label.pixmap().scaled(
                self.right.size(),
                Qt.KeepAspectRatioByExpanding,
                Qt.SmoothTransformation
            )
            self.background_label.setPixmap(scaled_pixmap)
            self.background_label.setGeometry(0, 0, self.right.width(), self.right.height())
        
        if hasattr(self, 'dim_overlay'):
            self.dim_overlay.setGeometry(0, 0, self.right.width(), self.right.height())
    
    def resizeEvent(self, event):
        """Handle window resize to update background"""
        super().resizeEvent(event)
        self.update_background_geometry()

        # Update settings page size to cover entire window
        if hasattr(self, 'settings_page'):
            self.settings_page.setGeometry(0, 0, self.width(), self.height())

    def update_forecast(self, data):
        """Update 5-day forecast display"""
        daily = data['daily'][:5]
        
        for i, day_data in enumerate(daily):
            if i < len(self.forecast_cards):
                card = self.forecast_cards[i]
                card.day_label.setText(day_data['day_name'][:3])
                card.temp_label.setText(self.format_temperature(day_data['temp_avg']))
                card.desc_label.setText(day_data['description'].title())
                icon = self.get_weather_emoji(day_data['description'])
                card.icon_label.setText(icon)
                
                # Load icon image
                icon_path = self.get_weather_icon_path(day_data['description'])
                if os.path.exists(icon_path):
                    pixmap = QPixmap(icon_path)
                    card.icon_label.setPixmap(pixmap)
                else:
                    # Fallback if image doesn't exist
                    card.icon_label.setText("🌤️")

    def get_weather_icon_path(self, description):
        """Map weather description to icon file path"""
        desc_lower = description.lower()
        if 'clear' in desc_lower:
            return 'assets/icons/sun.png'
        elif 'few clouds' in desc_lower or 'scattered' in desc_lower:
            return 'assets/icons/cloudy-day.png'
        elif 'cloud' in desc_lower:
            return 'assets/icons/cloud.png'
        elif 'rain' in desc_lower or 'drizzle' in desc_lower:
            return 'assets/icons/raindrops.png'
        elif 'thunder' in desc_lower or 'storm' in desc_lower:
            return 'assets/icons/storm.png'
        elif 'snow' in desc_lower:
            return 'assets/icons/snowflake.png'
        elif 'mist' in desc_lower or 'fog' in desc_lower:
            return 'assets/icons/fog.png'  # Reusing cloud icon for fog
        else:
            return 'assets/icons/cloudy-day.png'
        
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

        # Hide floating menu button
        self.floating_menu_button.hide()

        # Animate both minimum and maximum width for smooth animation
        self.sidebar_anim.setStartValue(self.sidebar.width())
        self.sidebar_anim.setEndValue(self.sidebar_expanded)
        self.sidebar_anim.start()
        
        self.sidebar_max_anim.setStartValue(self.sidebar.maximumWidth())
        self.sidebar_max_anim.setEndValue(self.sidebar_expanded)
        self.sidebar_max_anim.start()

    def collapse_sidebar(self):
        self.current_sidebar_width = self.sidebar_collapsed

        # Show floating menu button
        self.floating_menu_button.show()

        # Animate both minimum and maximum width for smooth animation
        self.sidebar_anim.setStartValue(self.sidebar.width())
        self.sidebar_anim.setEndValue(self.sidebar_collapsed)
        self.sidebar_anim.start()
        
        self.sidebar_max_anim.setStartValue(self.sidebar.maximumWidth())
        self.sidebar_max_anim.setEndValue(self.sidebar_collapsed)
        self.sidebar_max_anim.start()