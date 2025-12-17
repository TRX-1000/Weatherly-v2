import json
import os
from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
    QFrame, QLineEdit, QLabel, QScrollArea, QMenu, QAction, QGraphicsBlurEffect, QGridLayout, QSizePolicy
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QThread, pyqtSignal, QTimer, QPoint
from PyQt5.QtGui import QCursor, QPixmap

from ui.sidebar_card import WeatherCard
from ui.news_card import NewsCard
from ui.settings_page import SettingsPage

from tools.weather_api import WeatherAPI
from tools.news_api import NewsAPI
from tools.window_config import WindowConfig
from tools.location_detector import LocationWorker
\
from datetime import datetime, timezone, timedelta

# Dad jokes for easter egg
DAD_JOKES = [
    "Why did the weather report go to therapy? It had too many issues with precipitation!",
    "What's a tornado's favorite game? Twister!",
    "Why don't meteorologists ever win at poker? Everyone can read their forecasts!",
    "What did the cloud say to the lightning bolt? You're shocking!",
    "Why was the weatherman embarrassed? He made a mist-ake!",
    "What do you call it when it rains chickens and ducks? Fowl weather!",
    "How do hurricanes see? With one eye!",
    "What's the difference between weather and climate? You can't weather a tree, but you can climate!",
    "Why did the woman go outdoors with her purse open? She expected some change in the weather!",
    "What do you call a month's worth of rain? England!",
    "I tried telling a joke about the wind… but it blew.",
    "Why did the sun go to school? To get a little brighter!",
    "What do you call a snowman in the summer? A puddle!",
    "Why did the lightning bolt break up with the cloud? There was no spark!",
    "How does a raindrop keep its pants up? With a rain belt!",
    "Why don't mountains get cold in winter? …They wear snowcaps.",
    "I wanted to be a meteorologist… but my career never took off the ground.”",
    "Why was the fog so popular? Because it was down to earth!",
    "Why did the rainbow get promoted? …It brought a lot of color to the team.",
    "Click me again and I'll start charging a dew-ty fee.",

]

class SassySearchBar(QLineEdit):
    """Custom search bar with sass easter egg"""
    clicked = pyqtSignal()
    
    def mousePressEvent(self, event):
        """Override mouse press to emit signal"""
        self.clicked.emit()
        super().mousePressEvent(event)

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
        start_x = self.window_config.get_start_x()
        start_y = self.window_config.get_start_y()
        width = self.window_config.get_width()
        height = self.window_config.get_height()
        min_width = self.window_config.get_min_width()
        min_height = self.window_config.get_min_height()

        self.label_spacing = self.window_config.get_label_spacing()

        self.setGeometry(start_x, start_y, width, height)
        self.setMinimumSize(min_width, min_height)        

        # Initialize APIs
        self.weather_api = WeatherAPI("69ff8ccadbda20220e57e69ffad4a882")
        self.total_api_calls = 0
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

        self.use_24h = self.settings.get("time_format", "24h") == "24h"


        # Refresh button spam tracking
        self.refresh_click_count = 0
        self.refresh_click_timer = QTimer()
        self.refresh_click_timer.timeout.connect(self.reset_refresh_count)
        self.refresh_original_icon = "↻"

        # Setup refresh timer
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.auto_refresh_weather)
        self.setup_refresh_timer()

        # ---------------- MAIN LAYOUT ----------------
    
        self.sidebar_collapsed = 0
        self.sidebar_expanded = self.window_config.get_sidebar_opened()
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
        self.menu_button.setFixedSize(50, 50)
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
        sidebar_title.setStyleSheet("font-size: 25px; font-weight: bold; color: white;")

        header_layout.addWidget(self.menu_button)
        header_layout.addWidget(sidebar_title)
        header_layout.addStretch()

        # Search bar in sidebar
        search_container = QFrame()
        search_container.setStyleSheet("background-color: #1a1a1a;")
        search_layout = QVBoxLayout(search_container)
        search_layout.setContentsMargins(15, 5, 15, 15)

        self.search_bar = SassySearchBar()
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

        # Search bar sass tracking
        self.search_click_count = 0
        self.search_click_timer = QTimer()
        self.search_click_timer.timeout.connect(self.reset_search_click_count)
        self.original_placeholder = self.search_bar.placeholderText()
        # Connect click signal
        self.search_bar.clicked.connect(self.on_search_bar_clicked)
        # Track for developer mode

        self.dev_mode_active = False

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
        self.floating_menu_button.setFixedSize(50, 50)
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
        self.refresh_button.setFixedSize(50, 50)
        self.refresh_button.setStyleSheet("""
            QPushButton {
                background: #262626;
                border-radius: 10px;
                color: white;
                font-size: 24px;
            }
            QPushButton:hover { background: #333; }
        """)
        self.refresh_button.clicked.connect(self.on_refresh_clicked)

        self.settings_button = QPushButton("⚙️")
        self.settings_button.setFixedSize(50, 50)
        self.settings_button.setStyleSheet("""
            QPushButton {
                background: #262626;
                border-radius: 10px;
                color: white;
                font-size: 22px;
            }
            QPushButton:hover { background: #333; }""")
        
        self.settings_button.clicked.connect(self.open_settings)
        
        self.location_button = QPushButton("📍")
        self.location_button.setFixedSize(50, 50)
        self.location_button.setStyleSheet("""
            QPushButton {
                background: #262626;
                border-radius: 10px;
                color: white;
                font-size: 22px;
            }
            QPushButton:hover { background: #333; }
        """)
        self.location_button.clicked.connect(self.detect_location)
        self.location_button.setToolTip("Detect my location")


        top_bar_container.addWidget(self.floating_menu_button)
        top_bar_container.addStretch()
        top_bar_container.addWidget(self.location_button)
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
        self.content_layout.setSpacing(40)

        self.create_current_weather_section()

        self.create_forecast_section()

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
        self.settings_page.clear_cities.connect(self.clear_all_cities)
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
        self.location_button.raise_()
        self.scroll_area.raise_()

        # Animations
        self.sidebar_anim = QPropertyAnimation(self.sidebar, b"minimumWidth")
        self.sidebar_anim.setDuration(250)
        self.sidebar_anim.setEasingCurve(QEasingCurve.OutCubic)
        self.sidebar_anim.valueChanged.connect(self.update_background_geometry)
        
        self.sidebar_max_anim = QPropertyAnimation(self.sidebar, b"maximumWidth")
        self.sidebar_max_anim.setDuration(250)
        self.sidebar_max_anim.setEasingCurve(QEasingCurve.OutCubic)

        # Apply sidebar setting after everything is initialized
        self.apply_sidebar_setting()

        # Load default city or first saved city
        default_city = self.settings.get("default_city", "").strip()
        if default_city:
            self.search_bar.setText(default_city)
            self.search_weather()
        elif self.saved_cities:
            self.search_bar.setText(self.saved_cities[0])
            self.search_weather()

    # ---------------- City Persistence ----------------

    def detect_location(self):
        """Detect user's location and load weather"""
        # Change button to show loading
        self.location_button.setText("⏳")
        self.location_button.setEnabled(False)
        
        # Create worker thread
        self.location_worker = LocationWorker()
        self.location_worker.finished.connect(self.on_location_detected)
        self.location_worker.error.connect(self.on_location_error)
        self.location_worker.start()
    
    def on_location_detected(self, city):
        """Handle successful location detection"""
        self.location_button.setText("📍")
        self.location_button.setEnabled(True)
        
        # Load weather for detected city
        self.search_bar.setText(city)
        self.search_weather()
        
        print(f"Location detected: {city}")
    
    def on_location_error(self, error_msg):
        """Handle location detection error"""
        self.location_button.setText("📍")
        self.location_button.setEnabled(True)
        
        print(f"Location detection error: {error_msg}")
        
        # Show error message
        self.city_label.setText("Location Detection Failed")
        self.description_label.setText(error_msg)

    def setup_refresh_timer(self):
        """Setup auto-refresh timer based on settings"""
        self.refresh_timer.stop()
        
        interval = self.settings.get("refresh_interval", "manual")
        
        if interval != "manual":
            minutes = int(interval)
            milliseconds = minutes * 60 * 1000
            self.refresh_timer.start(milliseconds)
            print(f"Auto-refresh enabled: every {minutes} minutes")
        else:
            print("Auto-refresh disabled (manual mode)")

    
    def auto_refresh_weather(self):
        """Auto-refresh weather data"""
        print("Auto-refreshing weather data...")
        if self.current_city:
            self.search_weather()
        
        # Refresh all sidebar cities
        for city in self.saved_cities:
            self.fetch_city_weather(city)
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
        current_layout.setContentsMargins(0, 0, 0, 0)
        current_layout.setSpacing(15)

        self.city_label = QLabel("Select a city to view weather")
        self.city_label.setStyleSheet("font-size: 45px; font-weight: bold; color: white; background: none;")
        self.city_label.setAlignment(Qt.AlignCenter)
        
        self.temp_label = QLabel("--Â°C")
        self.temp_label.setStyleSheet("font-size: 120px; font-weight: bold; color: white; background: none;")
        self.temp_label.setAlignment(Qt.AlignCenter)
        
        self.description_label = QLabel("--")
        self.description_label.setStyleSheet("font-size: 32px; font-weight: bold; color: #fff; background: none;")
        self.description_label.setAlignment(Qt.AlignCenter)
        

        # Create info cards and add to grid
        self.feels_like_card = self.create_info_card(" Feels Like", "--Â°C")

        self.humidity_card = self.create_info_card(" Humidity", "--%")

        self.wind_card = self.create_info_card(" Wind Speed", "-- km/h")

        self.pressure_card = self.create_info_card(" Pressure", "-- hPa")

        self.clouds_card = self.create_info_card(" Cloudiness", "--%")

        self.precip_card = self.create_info_card(" Precipitation", "-- mm")

        self.visibility_card = self.create_info_card(" Visibility", "-- km")

        self.sunrise_card = self.create_info_card(" Sunrise", "--:--")

        self.sunset_card = self.create_info_card(" Sunset", "--:--")

        # Grid container for info cards
        info_container = QWidget()
        info_container.setStyleSheet("background: transparent;")
        info_container.setMaximumWidth(1000)
        info_grid = QGridLayout(info_container)
        info_grid.setContentsMargins(0, 0, 0, 0)
        info_grid.setVerticalSpacing(20)
        info_grid.setHorizontalSpacing(30)

        info_grid.addWidget(self.feels_like_card, 0, 0)
        info_grid.addWidget(self.humidity_card, 0, 1)
        info_grid.addWidget(self.wind_card, 0, 2)

        info_grid.addWidget(self.pressure_card, 1, 0)
        info_grid.addWidget(self.clouds_card, 1, 1)
        info_grid.addWidget(self.visibility_card, 1, 2)

        info_grid.addWidget(self.sunrise_card, 2, 0)
        info_grid.addWidget(self.sunset_card, 2, 1)
        info_grid.addWidget(self.precip_card, 2, 2)

        """ info_grid.setColumnStretch(0, 1)
        info_grid.setColumnStretch(1, 1)
        info_grid.setColumnStretch(2, 1) """

        current_layout.setAlignment(Qt.AlignCenter)
        current_layout.addWidget(self.city_label)
        current_layout.addWidget(self.temp_label)
        current_layout.addWidget(self.description_label)
        current_layout.addSpacing(30)
        current_layout.addWidget(info_container, alignment=Qt.AlignCenter)

        self.content_layout.addWidget(self.current_section)

    def create_info_card(self, title, value):
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.18);
                border-radius: 16px;
            }
        """)

        card.setMinimumHeight(85)
        card.setMaximumHeight(85)
        card.setMinimumWidth(260)  # Reduced from 250
        card.setMaximumWidth(260)  # Add this to limit growth

        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setAlignment(Qt.AlignCenter)

        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                background: transparent;
                border: none;
                font-size: 16px;
                color: #ddd;
            }
        """)
        title_label.setFrameStyle(QFrame.NoFrame)
        title_label.setAlignment(Qt.AlignCenter)

        value_label = QLabel(value)
        value_label.setStyleSheet("""
            QLabel {
                background: transparent;
                border: none;
                font-size: 25px;
                font-weight: bold;
                color: white;
            }
        """)
        value_label.setFrameStyle(QFrame.NoFrame)
        value_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(title_label)
        layout.addWidget(value_label)

        card.title_label = title_label
        card.value_label = value_label

        return card

    def create_forecast_section(self):
        """Create the 5-day forecast section"""
        forecast_header = QLabel("🗓️ 5-Day Forecast")
        forecast_header.setContentsMargins(self.label_spacing, 0, 0, 0)
        forecast_header.setStyleSheet("""
            font-size: 28px; 
            font-weight: bold; 
            color: white;
            padding-left: 5px;
        """)
        self.content_layout.addWidget(forecast_header)
        
        self.forecast_container = QFrame()
        self.forecast_container.setObjectName("forecastContainer")
        self.forecast_container.setStyleSheet("""
            QFrame#forecastContainer {
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.18);
                border-radius: 16px;
            }
        """)       
        
        self.forecast_container.setFixedWidth(850)  # Changed from setMaximumWidth
        
        self.forecast_layout = QHBoxLayout(self.forecast_container)
        self.forecast_layout.setSpacing(33)
        self.forecast_layout.setContentsMargins(20, 20, 20, 20)  # Internal padding for the glassmorphic box
        
        self.forecast_cards = []
        for i in range(5):
            card = self.create_forecast_card()
            self.forecast_cards.append(card)
            self.forecast_layout.addWidget(card)
        
        self.content_layout.addWidget(self.forecast_container, alignment=Qt.AlignCenter)

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
        
        icon_label = QLabel("ðŸŒ¤ï¸")
        icon_label.setStyleSheet("font-size: 52px; background: none;")
        icon_label.setAlignment(Qt.AlignCenter)
        
        temp_label = QLabel("--Â°")
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
        news_header.setContentsMargins(self.label_spacing, 0, 0, 0)
        news_header.setStyleSheet("""
            font-size: 26px; 
            font-weight: bold; 
            background: none;
            color: white;
            padding-left: 5px;
            margin-top: 10px;
        """)
        self.content_layout.addWidget(news_header)  # Keep header left-aligned
        
        # Create wrapper with HBoxLayout for centering
        news_wrapper = QWidget()
        news_wrapper.setStyleSheet("background: transparent;")
        news_wrapper_layout = QHBoxLayout(news_wrapper)
        news_wrapper_layout.setContentsMargins(0, 0, 0, 0)
        news_wrapper_layout.setSpacing(0)
        
        # Add left stretch
        news_wrapper_layout.addStretch()
        
        # News container - fixed width to match forecast
        self.news_container = QFrame()
        self.news_container.setStyleSheet("background: transparent;")
        self.news_container.setFixedWidth(850)  # Match forecast width exactly
        
        # News layout - NO margins to allow proper centering
        self.news_layout = QVBoxLayout(self.news_container)
        self.news_layout.setSpacing(15)
        self.news_layout.setContentsMargins(0, 0, 0, 0)  # CRITICAL: No left margin
        
        news_wrapper_layout.addWidget(self.news_container)
        
        # Add right stretch
        news_wrapper_layout.addStretch()
        
        # Add wrapper to content layout
        self.content_layout.addWidget(news_wrapper)

    # ---------------- Weather Data Fetching ----------------
    def load_saved_cities(self):
        """Load weather cards for saved cities"""
        for city in self.saved_cities:
            self.create_city_card(city)
    
    def create_city_card(self, city):
        """Create a city card with all event handlers"""
        card = WeatherCard(city)
        card.city_name = city
        card.click_count = 0
        card.last_click_time = 0
        
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
                import time
                current_time = time.time()
                
                # Reset if more than 1 second between clicks
                if current_time - card.last_click_time > 1.0:
                    card.click_count = 0
                
                card.click_count += 1
                card.last_click_time = current_time
                
                # Triple click = dad joke!
                if card.click_count == 3:
                    self.show_dad_joke(card)
                    card.click_count = 0
                else:
                    # Normal click - load weather
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
            "id": w["id"],
            "wind_speed": data["wind"]["speed"],
            "wind_deg": data["wind"].get("deg", 0),
            "clouds": data["clouds"]["all"],
            "visibility": data.get("visibility", 10000),  # ADD THIS LINE
            "timestamp": data["dt"],
            "sunrise": data["sys"]["sunrise"],
            "sunset": data["sys"]["sunset"],
            "timezone": data["timezone"]
        }
    
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
        
        # Check for developer mode secret code
        if city.lower() == "dev.weather.debug.mode.enable":
            self.open_developer_settings()
            self.search_bar.clear()
            return
        
        # Check for Channel 42 easter egg
        if city.lower() == "channel 42":
            self.show_channel_42()
            self.search_bar.clear()
            return
        
        try:
            self.current_city = city
            
            # Add city to sidebar if not already there
            self.add_city_to_sidebar(city)
            
            # Fetch current weather
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

    def clear_all_cities(self):
        """Clear all saved cities from sidebar"""
        # Clear the list
        self.saved_cities.clear()
        self.save_cities_to_file()
        
        # Remove all cards from UI
        for city, card in list(self.city_cards.items()):
            self.sidebar_layout.removeWidget(card)
            card.deleteLater()
        
        self.city_cards.clear()
        
        # Clear current weather display
        self.current_city = None
        self.city_label.setText("Select a city to view weather")
        self.temp_label.setText("--°C")
        self.description_label.setText("--")
        self.feels_like_label.setText("Feels like: --°C")
        self.humidity_label.setText("Humidity: --%")
        self.wind_label.setText("Wind: -- m/s")
        self.pressure_label.setText("Pressure: -- hPa")
        self.clouds_label.setText("Clouds: --%")
        self.sunrise_label.setText("Sunrise: --:--")
        self.sunset_label.setText("Sunset: --:--")
        self.clear_news()
        
        # Clear forecast
        for card in self.forecast_cards:
            card.day_label.setText("--")
            card.temp_label.setText("--°")
            card.desc_label.setText("--")
            card.icon_label.setText("🌤️")
        
        # Reset background
        self.right.setStyleSheet("background-color: #111;")
        if hasattr(self, 'background_label'):
            self.background_label.clear()
        
        # Clear search bar
        self.search_bar.clear()

    
    def open_developer_settings(self):
        """Open developer settings easter egg"""
        from PyQt5.QtWidgets import QDialog, QTextEdit
        import psutil
        import os
        from datetime import datetime, timedelta
            
        dialog = QDialog(self)
        dialog.setWindowTitle("🔧 Developer Console")
        dialog.setModal(True)
        dialog.setFixedSize(600, 500)
        dialog.setStyleSheet("background-color: #0a0a0a;")
            
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
            
        title = QLabel("⚙️ DEVELOPER MODE ACTIVATED")
        title.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            color: #00ff00;
            padding: 10px;
            font-family: 'Courier New', monospace;
        """)
        title.setAlignment(Qt.AlignCenter)
            
        # Info display
        info_text = QTextEdit()
        info_text.setReadOnly(True)
        info_text.setStyleSheet("""
            QTextEdit {
                background-color: #1a1a1a;
                color: #00ff00;
                border: 2px solid #00ff00;
                border-radius: 8px;
                padding: 15px;
                font-family: 'Courier New', monospace;
                font-size: 13px;
            }
        """)
            
        # Get REAL system and app information
        try:
            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / (1024 * 1024)
            cpu_percent = process.cpu_percent(interval=0.1)
                
            # Calculate app uptime
            create_time = datetime.fromtimestamp(process.create_time())
            uptime = datetime.now() - create_time
            uptime_str = str(uptime).split('.')[0]  # Remove microseconds
                
        except:
            memory_mb = 0
            cpu_percent = 0
            uptime_str = "Unknown"
            
        # Real API call tracking (you'll need to add this)
        api_calls_made = getattr(self, 'total_api_calls', 0)
            
        # Calculate cache size
        cache_size_mb = 0
        try:
            if os.path.exists(self.cities_file):
                cache_size_mb += os.path.getsize(self.cities_file) / (1024 * 1024)
            if os.path.exists(self.settings_file):
                cache_size_mb += os.path.getsize(self.settings_file) / (1024 * 1024)
        except:
            pass
            
        # Count Easter eggs found
        easter_eggs_found = 0
        if hasattr(self, 'dev_mode_active') and self.dev_mode_active:
            easter_eggs_found += 1
        if hasattr(self, 'channel_42_found') and self.channel_42_found:
            easter_eggs_found += 1
            
        # Get refresh interval setting
        refresh_interval = self.settings.get("refresh_interval", "manual")
        if refresh_interval == "manual":
            refresh_status = "MANUAL (Disabled)"
        else:
            refresh_status = f"EVERY {refresh_interval} MINUTES"
            
        # Current weather API info
        current_city = self.current_city if self.current_city else "None"
        
        dev_info = f"""
    ╔════════════════════════════════════════════╗
    ║         WEATHERLY DEVELOPER CONSOLE        ║
    ╚════════════════════════════════════════════╝

    [SYSTEM STATUS]
    ├─ Status: OPERATIONAL ✓
    ├─ Version: 2.0.0
    ├─ Build: PRODUCTION
    ├─ Uptime: {uptime_str}
    └─ Platform: {self.window_config.get_platform_name()}

    [API STATISTICS]
    ├─ Total Calls Made: {api_calls_made:,}
    ├─ API Key: {'*' * 28}{self.weather_api.api_key[-4:]}
    ├─ Current City: {current_city}
    ├─ Saved Cities: {len(self.saved_cities)}
    └─ Auto-Refresh: {refresh_status}

    [CACHE & STORAGE]
    ├─ Cache Size: {cache_size_mb:.2f} MB
    ├─ Cities File: {self.cities_file}
    ├─ Settings File: {self.settings_file}
    └─ Config Files: 3 loaded

    [PERFORMANCE METRICS]
    ├─ Memory Usage: {memory_mb:.1f} MB
    ├─ CPU Usage: {cpu_percent:.1f}%
    ├─ Active Workers: {len(getattr(self, 'workers', []))}
    └─ News Workers: {len(self.news_workers)}

    [CURRENT SETTINGS]
    ├─ Temperature: {self.settings.get('temperature_unit', 'celsius').upper()}
    ├─ Wind Speed: {self.settings.get('wind_unit', 'metric').upper()}
    ├─ News Count: {self.settings.get('news_count', '10')} articles
    ├─ Default City: {self.settings.get('default_city', 'None') or 'None'}
    └─ Refresh: {refresh_interval}

    [WINDOW CONFIGURATION]
    ├─ Size: {self.width()}x{self.height()}
    ├─ Min Size: {self.minimumWidth()}x{self.minimumHeight()}
    ├─ Sidebar: {'Expanded' if self.current_sidebar_width > 0 else 'Collapsed'}
    └─ Position: ({self.x()}, {self.y()})

    [EASTER EGGS DISCOVERED]
    ├─ Developer Mode: ✓ (You're here!)
    ├─ Channel 42: {'✓' if hasattr(self, 'channel_42_found') else '✗'}
    ├─ Dad Jokes: {'✓' if any(hasattr(card, 'click_count') for card in self.city_cards.values()) else '✗'}
    ├─ Refresh Spam: {'✓' if hasattr(self, 'refresh_click_count') else '✗'}
    ├─ Search Sass: {'✓' if hasattr(self, 'search_click_count') else '✗'}
    ├─ Color Invert: {'✓' if hasattr(self, 'inverted_mode') else '✗'}
    └─ Total Found: {easter_eggs_found}/8

    [DEBUG LOG]
    > Weather API initialized: ✓
    > Location detector ready: ✓
    > News feed operational: ✓
    > Settings loaded: ✓
    > All systems nominal: ✓

    [DEVELOPER INFO]
    GitHub: https://github.com/TRX-1000/Weatherly-v2
    API: OpenWeatherMap v2.5
    Framework: PyQt5
            """
            
        info_text.setText(dev_info)
            
        close_btn = QPushButton("✓ Close Console")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #00ff00;
                color: #000;
                border: none;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Courier New', monospace;
            }
            QPushButton:hover {
                background-color: #00cc00;
            }
        """)
        close_btn.clicked.connect(dialog.close)
            
        layout.addWidget(title)
        layout.addWidget(info_text)
        layout.addWidget(close_btn)
            
        dialog.exec_()
            
        # Mark as found
        self.dev_mode_active = True

    def on_search_bar_clicked(self):
        """Handle search bar clicks for sass easter egg"""
        # Only count if search bar is empty
        if not self.search_bar.text().strip():
            self.search_click_count += 1
            
            # Restart timer (3 seconds to reset)
            self.search_click_timer.stop()
            self.search_click_timer.start(3000)
                        
            if self.search_click_count >= 5:
                self.show_search_bar_sass()
    
    def show_search_bar_sass(self):
        """Show sassy placeholder text"""
        sassy_messages = [
            "I'm waiting... 🙄",
            "Hello? Anyone there? 👋",
            "Type something already! ⌨️",
            "This is awkward... 😬",
            "Still waiting... ⏰",
            "Are you okay? 🤔",
            "Looking for something? 👀",
            "Don't be shy, type a city! 🌍",
            "You know you want to... 😏",
            "Is typing hard? Let me help! 🖊️",
            "C'mon, give me a city! 🏙️",
            "I'm not just decoration! 🎨",
            "Wow, someone's impatient today! 😤",
            "Keep shredding bro. 🔥",
            "Why'd you choose violence? 😈",
            "Deleting search_bar.exe...🗑️"
        ]
        
        import random
        sassy_text = random.choice(sassy_messages)
        self.search_bar.setPlaceholderText(sassy_text)
        
        # Reset click count
        self.search_click_count = 0
        
        # Reset placeholder after 5 seconds
        QTimer.singleShot(5000, self.reset_search_placeholder)
    
    def reset_search_placeholder(self):
        """Reset search bar placeholder to original"""
        self.search_bar.setPlaceholderText(self.original_placeholder)
    
    def reset_search_click_count(self):
        """Reset search click counter"""
        self.search_click_count = 0
        self.search_click_timer.stop()

    def show_channel_42(self):
        """Show Channel 42 secret weather channel"""
        import random
        
        # Absurd fictional locations
        locations = [
            ("Gotham City", "Stormy with 80% chance of Batman", "⚡🦇", -5, 12),
            ("Hogwarts", "Dementors moving in from the north", "🌫️✨", 3, 8),
            ("Mordor", "One does not simply walk into this forecast", "🌋👁️", 45, 52),
            ("Atlantis", "Wet. Very wet. Surprisingly wet.", "🌊🧜", 18, 20),
            ("Narnia", "Always winter, never Christmas", "❄️🦁", -15, -10),
            ("Springfield", "D'oh! Partly cloudy", "☁️🍩", 22, 28),
            ("Bikini Bottom", "Perfect weather for jellyfishing!", "🌊🍔", 12, 15),
            ("Asgard", "Worthy thunderstorms expected", "⚡🔨", 8, 14),
            ("Death Star", "No weather. It's a space station.", "⭐💀", -273, -273),
            ("Emerald City", "Follow the yellow brick road to sunshine", "🌈👠", 24, 30),
            ("Silent Hill", "Fog advisory in effect... forever", "🌫️😱", 10, 15),
            ("Twin Peaks", "Damn fine weather with coffee", "☕🌲", 15, 20),
            ("Westeros", "Winter is coming (as usual)", "❄️⚔️", -5, 5),
            ("Jurassic Park", "Clever girl... the storm is here", "🦖⛈️", 30, 35),
            ("The Upside Down", "Extremely strange things", "🙃👾", 666, 666),
        ]
        
        location = random.choice(locations)
        city_name, description, emoji, temp_min, temp_max = location
        temp = random.randint(temp_min, temp_max)
        
        # Update display with absurd data
        self.city_label.setText(f"📺 CHANNEL 42: {city_name}")
        self.temp_label.setText(f"{temp}°C {emoji}")
        self.description_label.setText(description)
        
        # Add absurd details
        self.feels_like_label.setText(f"Feels like: Absolutely unreal")
        self.humidity_label.setText(f"Humidity: {random.randint(0, 200)}%")
        self.wind_label.setText(f"Wind: {random.choice(['Mild', 'Dragon breath', 'Existential', 'Yes'])}")
        self.pressure_label.setText(f"Pressure: {random.randint(1, 9999)} hopes/dreams")
        self.clouds_label.setText(f"Clouds: {random.choice(['Fluffy', 'Ominous', 'Pixelated', 'Sentient'])} ")
        self.sunrise_label.setText(f"🌅 Sunrise: {random.choice(['Never', 'Always', '??:??', 'Quantum'])}")
        self.sunset_label.setText(f"🌇 Sunset: {random.choice(['Maybe', 'Depends', 'Ask later', '42:00'])}")
        
        # Clear forecast and news
        for card in self.forecast_cards:
            card.day_label.setText(random.choice(["Mon?", "Tues!", "Nope", "Maybe", "Soon"]))
            card.temp_label.setText(f"{random.randint(-50, 100)}°")
            card.desc_label.setText(random.choice([
                "Chaos", "Mystery", "???", "Uncertain", "Glitchy", "Legendary"
            ]))
            card.icon_label.setText(random.choice(["❓", "🎲", "🎪", "🎭", "🎰", "🃏"]))
        
        self.clear_news()
        
        # Mark as found
        self.channel_42_found = True
        
        # Show notification
        from PyQt5.QtWidgets import QMessageBox
        msg = QMessageBox(self)
        msg.setWindowTitle("📺 Channel 42")
        msg.setText("Welcome to Channel 42!\n\n"
                   "The weather channel that doesn't exist...\n"
                   "Broadcasting from locations that may or may not be real.\n\n"
                   "Don't tell anyone about this. 🤫")
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #1a1a1a;
            }
            QMessageBox QLabel {
                color: white;
                font-size: 14px;
            }
            QPushButton {
                background-color: #5ba3ff;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 20px;
                font-size: 14px;
                min-width: 80px;
            }
        """)
        msg.exec_()
    def reset_refresh_count(self):
        self.refresh_click_count = 0
        self.refresh_button.setText(self.refresh_original_icon)

    def on_refresh_clicked(self):
        """Handle refresh button clicks with easter egg"""
        self.refresh_click_count += 1
        
        # Restart timer (2 seconds to reset count)
        self.refresh_click_timer.stop()
        self.refresh_click_timer.start(2000)
        
        if self.refresh_click_count == 5:
            # Change icon
            self.refresh_button.setText("🔄")
            self.refresh_weather()
            
        elif self.refresh_click_count == 10:
            # Show message
            self.refresh_button.setText("😤")
            self.show_refresh_warning()
            
        elif self.refresh_click_count >= 15:
            # Button takes off!
            self.refresh_button_takeoff()
            self.refresh_click_count = 0
        else:
            # Normal refresh
            self.refresh_weather()
    
    def show_refresh_warning(self):
        """Show warning message for excessive refreshing"""
        from PyQt5.QtWidgets import QLabel
        
        warning = QLabel("That's enough refreshing! The weather doesn't change that fast! 🙄", self)
        warning.setStyleSheet("""
            QLabel {
                background-color: rgba(255, 100, 100, 230);
                color: white;
                padding: 15px 25px;
                border-radius: 12px;
                font-size: 15px;
                font-weight: bold;
                border: 2px solid #ff6b6b;
            }
        """)
        warning.adjustSize()
        warning.move(
            (self.width() - warning.width()) // 2,
            self.height() // 2 - 100
        )
        warning.show()
        warning.raise_()
        
        # Remove after 3 seconds
        QTimer.singleShot(3000, warning.deleteLater)
    
    def refresh_button_takeoff(self):
        """Make refresh button fly away"""
        # Disable button during animation
        self.refresh_button.setEnabled(False)
        self.refresh_button.setText("🚀")
        
        # Store original position
        original_pos = self.refresh_button.pos()
        
        # Create animation
        self.refresh_takeoff_anim = QPropertyAnimation(self.refresh_button, b"pos")
        self.refresh_takeoff_anim.setDuration(2000)
        self.refresh_takeoff_anim.setStartValue(original_pos)
        
        # Random end position (off screen)
        import random
        end_x = random.choice([-100, self.width() + 100])
        end_y = random.randint(-100, self.height() + 100)
        self.refresh_takeoff_anim.setEndValue(self.refresh_button.mapToParent(
            self.refresh_button.rect().topLeft()) + QPoint(end_x, end_y))
        
        self.refresh_takeoff_anim.setEasingCurve(QEasingCurve.InOutQuad)
        
        # Add rotation animation
        self.refresh_button.setStyleSheet(self.refresh_button.styleSheet())
        
        # When finished, reset
        self.refresh_takeoff_anim.finished.connect(self.reset_refresh_button)
        self.refresh_takeoff_anim.start()
        
        # Show message
        from PyQt5.QtWidgets import QLabel
        takeoff_msg = QLabel("Houston, we have liftoff! 🚀✨", self)
        takeoff_msg.setStyleSheet("""
            QLabel {
                background-color: rgba(74, 143, 255, 230);
                color: white;
                padding: 15px 25px;
                border-radius: 12px;
                font-size: 16px;
                font-weight: bold;
                border: 2px solid #5ba3ff;
            }
        """)
        takeoff_msg.adjustSize()
        takeoff_msg.move(
            (self.width() - takeoff_msg.width()) // 2,
            self.height() // 2
        )
        takeoff_msg.show()
        takeoff_msg.raise_()
        
        QTimer.singleShot(2500, takeoff_msg.deleteLater)
    
    def reset_refresh_button(self):
        """Reset refresh button to original position"""
        # Small delay for dramatic effect
        QTimer.singleShot(1000, self._actually_reset_refresh_button)
    
    def _actually_reset_refresh_button(self):
        """Actually reset the button"""
        self.refresh_button.setText(self.refresh_original_icon)
        self.refresh_button.setEnabled(True)
        
        # Get the parent layout and re-add button
        # We need to find its original position in the layout
        # For now, just set it back to a reasonable position
        self.refresh_button.move(self.refresh_button.parent().width() - 60, 15)
        
        # Show "welcome back" message
        from PyQt5.QtWidgets import QLabel
        welcome_msg = QLabel("Welcome back, refresh button! 👋", self)
        welcome_msg.setStyleSheet("""
            QLabel {
                background-color: rgba(90, 200, 90, 230);
                color: white;
                padding: 12px 20px;
                border-radius: 10px;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        welcome_msg.adjustSize()
        welcome_msg.move(
            self.width() - welcome_msg.width() - 20,
            80
        )
        welcome_msg.show()
        welcome_msg.raise_()
        
        QTimer.singleShot(2000, welcome_msg.deleteLater)
    
    def reset_refresh_count(self):
        """Reset refresh click counter"""
        if self.refresh_click_count > 0 and self.refresh_click_count < 15:
            self.refresh_button.setText(self.refresh_original_icon)
        self.refresh_click_count = 0
        self.refresh_click_timer.stop()

    def show_dad_joke(self, card):
        """Show a random dad joke"""
        import random
        from PyQt5.QtWidgets import QLabel
        
        joke = random.choice(DAD_JOKES)
        
        # Create floating joke label
        joke_label = QLabel(joke, self)
        joke_label.setStyleSheet("""
            QLabel {
                background-color: rgba(90, 163, 255, 240);
                color: white;
                padding: 20px 25px;
                border-radius: 15px;
                font-size: 15px;
                font-weight: 600;
                border: 3px solid #4a8fff;
            }
        """)
        joke_label.setWordWrap(True)
        joke_label.setMaximumWidth(400)
        joke_label.adjustSize()
        
        # Position near the card
        global_pos = card.mapToGlobal(card.rect().center())
        local_pos = self.mapFromGlobal(global_pos)
        
        joke_label.move(
            max(10, min(local_pos.x() - joke_label.width() // 2, self.width() - joke_label.width() - 10)),
            max(10, min(local_pos.y() - joke_label.height() - 20, self.height() - joke_label.height() - 10))
        )
        
        joke_label.show()
        joke_label.raise_()
        
        # Fade out and remove after 4 seconds
        QTimer.singleShot(4000, joke_label.deleteLater)

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
            "auto_refresh": True,
            "default_city": "",
            "news_count": "10",
            "refresh_interval": "manual"
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

        # Update 12/24h preference
        self.use_24h = self.settings.get("time_format", "24h") == "24h"

        self.setup_refresh_timer()
        
        # Refresh weather with new units if a city is loaded
        if self.current_city:
            self.refresh_weather()
        
        # Update sunrise/sunset labels if current weather is loaded
        if hasattr(self, "current_weather_data") and self.current_weather_data:
            self.update_current_weather(self.current_weather_data)


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
    
    def format_local_time(self, utc_ts, tz_offset, use_24h):
        local_dt = datetime.fromtimestamp(utc_ts, tz=timezone.utc) + timedelta(seconds=tz_offset)
        return local_dt.strftime("%H:%M" if use_24h else "%I:%M %p")
    
    def format_precipitation(self, data):
        rain = data.get("rain", {}).get("1h", 0)
        snow = data.get("snow", {}).get("1h", 0)

        if rain > 0 and snow > 0:
            return "Mixed", f"Rain: {rain:.1f} mm\nSnow: {snow:.1f} mm"

        if rain > 0:
            return "Rain", f"{rain:.1f} mm"

        if snow > 0:
            return "Snow", f"{snow:.1f} mm"

        return "Precipitation", "—"

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
            no_news_label = QLabel("🔭 No recent weather news found for this location.")
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
        
        # Get news count from settings
        news_count = int(self.settings.get("news_count", "10"))
        
        # Limit news items to the configured count
        for item in news_items[:news_count]:
            news_card = NewsCard(
                item["title"],
                item["source"],
                item["published"],
                item["summary"],
                item["link"]
            )

            news_card.setMaximumWidth(850)
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
        self.city_label.setText(f"{data['city']}, {data['country']}")
        self.temp_label.setText(self.format_temperature(data["temperature"]))
        self.description_label.setText(data["description"].title())

        # Info cards
        self.feels_like_card.value_label.setText(
            self.format_temperature(data["feels_like"])
        )
        self.humidity_card.value_label.setText(f"{data['humidity']}%")
        self.wind_card.value_label.setText(
            self.format_wind_speed(data["wind_speed"])
        )
        self.pressure_card.value_label.setText(f"{data['pressure']} hPa")
        self.clouds_card.value_label.setText(f"{data['clouds']}%")

        # Visibility (meters → km)
        visibility_km = data["visibility"] / 1000
        self.visibility_card.value_label.setText(f"{visibility_km:.1f} km")

        # Precipitation
        title, value = self.format_precipitation(data)
        self.precip_card.title_label.setText(title)
        self.precip_card.value_label.setText(value)

        # Sunrise / Sunset (local time)
        self.sunrise_card.value_label.setText(
            self.format_local_time(data["sunrise"], data["timezone"], self.use_24h)
        )
        self.sunset_card.value_label.setText(
            self.format_local_time(data["sunset"], data["timezone"], self.use_24h)
        )

        # Background
        self.update_background(data.get("id", 800))

        
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

    def apply_sidebar_setting(self):
        """Apply the saved sidebar setting"""
        sidebar_setting = self.settings.get("sidebar_default", "expanded")
        
        if sidebar_setting == "collapsed":
            self.collapse_sidebar()
        # If "expanded" or "remember", sidebar is already expanded by default