from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QFrame, QRadioButton, QButtonGroup, QScrollArea, QLineEdit, QMessageBox, QGridLayout
)
from PyQt5.QtCore import Qt, pyqtSignal, QUrl
from PyQt5.QtGui import QDesktopServices, QCursor


class SettingsPage(QWidget):
    settings_changed = pyqtSignal(dict)
    back_clicked = pyqtSignal()
    clear_cities = pyqtSignal()
    
    def __init__(self, parent=None, current_settings=None):
        super().__init__(parent)
        
        # Load current settings or use defaults
        self.settings = current_settings or {
            "temperature_unit": "celsius",
            "wind_unit": "metric",
            "auto_refresh": True,
            "default_city": "",
            "news_count": "10",
            "refresh_interval": "manual",
            "sidebar_default": "remember",
            "notifs": "hi",
            "pressure_unit": "hpa",
            "time_format": "24h",
            "location_services": "enabled",
            "precipitation_unit": "mm"
        }
        
        self.setStyleSheet("background-color: #111;")
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Top bar with back button - Glassmorphic style
        top_bar = QFrame()
        top_bar.setStyleSheet("""
            QFrame {
                background: #111;
                border-bottom: 1px solid #2a2a2a;
            }
        """)
        top_bar.setFixedHeight(80)
        
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(30, 20, 30, 20)
        

        # Preferences Section Header
        prefs_header = QLabel("🎛️ Preferences")
        prefs_header.setStyleSheet("""
            font-size: 32px; 
            font-weight: bold; 
            color: white;
            border: none;
            margin-bottom: 0px;
            letter-spacing: -0.5px;
        """)

         # Done button at top right
        done_btn = QPushButton("✅ Done")
        done_btn.setCursor(QCursor(Qt.PointingHandCursor))
        done_btn.setFixedSize(140, 50)
        done_btn.setStyleSheet("""
            QPushButton {
                background: #1f1f1f;
                color: white;
                border: none;
                border-radius: 12px;
                margin-bottom: 5px;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #2d2d2d;
            }
        """)        

        done_btn.clicked.connect(self.on_back_clicked)
        top_layout.addStretch(1)
        top_layout.addWidget(prefs_header)
        top_layout.addStretch(50)
        top_layout.addWidget(done_btn)
        top_layout.addStretch(2)
        
        main_layout.addWidget(top_bar)
        
        # Scrollable content area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #111;
            }
            QScrollBar:vertical {
                background: #1a1a1a;
                width: 12px;
                border-radius: 6px;
                margin: 2px;
            }
        """)
        
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: #111;")
        
        layout = QVBoxLayout(scroll_content)
        layout.setContentsMargins(50, 40, 50, 50)
        layout.setSpacing(35)

        # Create cards and add to grid (2 columns)
        self.temp_card = self.create_setting_card(
            "🌡️ Temperature Unit",
            "Choose your preferred temperature scale",
            [("Celsius (°C)", "celsius"), ("Fahrenheit (°F)", "fahrenheit")],
            "temperature_unit"
        )
        
        self.wind_card = self.create_setting_card(
            "💨 Wind Speed Unit",
            "Choose your preferred wind speed measurement",
            [("Meters per second (m/s)", "metric"), ("Miles per hour (mph)", "imperial"), ("Kilometers per hour (kmph)", "kmph")],
            "wind_unit"
        )
        
        self.news_card = self.create_setting_card(
            "📰 News Articles",
            "Number of weather news articles to display",
            [("5 articles", "5"), ("10 articles", "10"), ("15 articles", "15")],
            "news_count"
        )
        
        self.default_city_card = self.create_text_input_card(
            "🏠 Default City",
            "City to load on startup (leave empty for last viewed)",
            "default_city"
        )
        
        self.refresh_card = self.create_setting_card(
            "🔄 Auto-Refresh Interval",
            "How often to update weather data automatically",
            [("Manual only", "manual"), ("Every 15 minutes", "15"), ("Every 30 minutes", "30"), ("Every hour", "60")],
            "refresh_interval"
        )

        self.pressure_card = self.create_setting_card(
            "📉 Pressure Unit",
            "Choose your preferred pressure measurement",
            [("Hectopascal (hPa)", "hpa"), ("Inches of Mercury (inHg)", "inhg"), ("Millimeters of Mercury (mmHg)", "mmhg")],
            "pressure_unit"
        )

        self.sunrise_sunset_card = self.create_setting_card(
            "🌅 Sunrise/Sunset Time Format",
            "Choose your preferred time format for sunrise and sunset",
            [("24-hour format", "24h"), ("12-hour format (AM/PM)", "12h")],
            "time_format"
        )

        self.location_services_card = self.create_setting_card(
            "📍 Location Services",
            "Enable or disable location services for automatic city detection",
            [("Enable Location Services", "enabled"), ("Disable Location Services", "disabled")],
            "location_services"
        )

        self.precipitation_card = self.create_setting_card(
            "🌧️ Precipitation Unit",
            "Choose your preferred precipitation measurement",
            [("Millimeters (mm)", "mm"), ("Inches (in)", "in")],
            "precipitation_unit"
        )

        self.notifications_card = self.create_setting_card(
            "🔔 Manage notifications",
            "Choose your preferred notifications settings",
            [("High priority", "hi"), ("Default", "mid"), ("Turn off notifications", "off")],
            "notifs"
        )

        self.sidebar_state_card = self.create_setting_card(
        "📌 Sidebar on Startup",
        "Choose the default sidebar state when app opens",
        [("Always expanded", "expanded"), ("Always collapsed", "collapsed"), ("Remember last state", "remember")],
        "sidebar_default"
        )

        # Clear Cities Card - with button instead of radio
        self.clear_cities_card = QFrame()
        self.clear_cities_card.setStyleSheet("""
            QFrame {
                background: #1a1a1a;
                border: 1px solid #2a2a2a;
                border-radius: 20px;
            }
        """)
        self.clear_cities_card.setMinimumHeight(280)

        clear_card_layout = QVBoxLayout(self.clear_cities_card)
        clear_card_layout.setContentsMargins(25, 25, 25, 25)
        clear_card_layout.setSpacing(15)

        clear_title = QLabel("🗑️ Clear All Saved Cities")
        clear_title.setStyleSheet("""
            font-size: 24px; 
            font-weight: 600; 
            color: white;
            border: none;
            letter-spacing: -0.3px;
            background: none;
        """)

        clear_desc = QLabel("Remove all saved cities from the application")
        clear_desc.setStyleSheet("""
            font-size: 16px;
            color: #888;
            border: none;
            background: none;
            margin-bottom: 10px;
        """)
        clear_desc.setWordWrap(True)

        clear_btn = QPushButton("Clear All Cities")
        clear_btn.setCursor(QCursor(Qt.PointingHandCursor))
        clear_btn.setFixedHeight(50)
        clear_btn.setStyleSheet("""
            QPushButton {
                background: #ff6565;
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #ff7575;
            }
            QPushButton:pressed {
                background: #ee5555;
            }
        """)
        clear_btn.clicked.connect(self.clear_all_cities)

        clear_card_layout.addWidget(clear_title)
        clear_card_layout.addWidget(clear_desc)
        clear_card_layout.addWidget(clear_btn)
        clear_card_layout.addStretch()
        # ---------------------------
        # GRID CONTAINER FOR UNITS
        # ---------------------------
        units_container = QWidget()
        units_container.setStyleSheet("background: transparent;")
        units_grid = QGridLayout(units_container)
        units_grid.setSpacing(20)
        units_grid.setContentsMargins(0, 0, 0, 0)

        # Units cards
        units_grid.addWidget(self.temp_card, 0, 0)
        units_grid.addWidget(self.wind_card, 0, 1)
        units_grid.addWidget(self.pressure_card, 1, 0)
        units_grid.addWidget(self.precipitation_card, 1, 1)

        units_grid.setColumnStretch(0, 1)
        units_grid.setColumnStretch(1, 1)

        # Units header
        u_and_m_section = QLabel("🌡️ Units & Measurements")
        u_and_m_section.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
            color: white;
            margin-bottom: 0px;
            letter-spacing: -0.5px;
        """)
        layout.addWidget(u_and_m_section)
        layout.addWidget(units_container)

        # ---------------------------
        # GRID CONTAINER FOR APP SETTINGS
        # ---------------------------
        app_container = QWidget()
        app_container.setStyleSheet("background: transparent;")
        app_grid = QGridLayout(app_container)
        app_grid.setSpacing(20)
        app_grid.setContentsMargins(0, 0, 0, 0)

        # App setting cards
        app_grid.addWidget(self.default_city_card,     0, 0)
        app_grid.addWidget(self.refresh_card,          0, 1)
        app_grid.addWidget(self.news_card,             1, 0)
        app_grid.addWidget(self.notifications_card,    1, 1)
        app_grid.addWidget(self.sunrise_sunset_card,   2, 0)
        app_grid.addWidget(self.sidebar_state_card,    2, 1)

        app_grid.setColumnStretch(0, 1)
        app_grid.setColumnStretch(1, 1)
        

        # App settings header
        a_s_section = QLabel("🛠️ App Settings")
        a_s_section.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
            color: white;
            margin-bottom: 0px;
            letter-spacing: -0.5px;
        """)
        layout.addWidget(a_s_section)
        layout.addWidget(app_container)

        layout.addSpacing(20)

        
        # ---------------------------
        # GRID CONTAINER FOR DATA MANAGEMENT
        # ---------------------------
        data_container = QWidget()
        data_container.setStyleSheet("background: transparent;")
        data_grid = QGridLayout(data_container)
        data_grid.setSpacing(20)
        data_grid.setContentsMargins(0, 0, 0, 0)

        # Data management cards
        data_grid.addWidget(self.location_services_card, 0, 0)
        data_grid.addWidget(self.clear_cities_card, 0, 1)

        data_grid.setColumnStretch(0, 1)
        data_grid.setColumnStretch(1, 1)

        # Data Management header
        d_m_section = QLabel("📦 Data Management")
        d_m_section.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
            color: white;
            margin-bottom: 0px;
            letter-spacing: -0.5px;
        """)
        layout.addWidget(d_m_section)
        layout.addWidget(data_container)

        layout.addSpacing(20)

        about_label = QLabel("ℹ About Weatherly")
        about_label.setStyleSheet("""
            font-size: 32px; 
            font-weight: bold; 
            color: white;
            border: none;
            margin-top: 10px;
            margin-bottom: 10px;
            letter-spacing: -0.5px;
        """)
        layout.addWidget(about_label)

        about_frame = QFrame()
        about_frame.setStyleSheet("""
            QFrame {
                background: #1a1a1a;
                border: 1px solid #2a2a2a;
                border-radius: 20px;
            }
        """)

        about_layout = QVBoxLayout(about_frame)
        about_layout.setSpacing(18)
        about_layout.setContentsMargins(30, 30, 30, 30)

        # App name - subtle and clean
        app_name = QLabel("Weatherly v2.0")
        app_name.setStyleSheet("""
            font-size: 28px; 
            font-weight: bold; 
            color: white; 
            background: none;
            border: none;
            letter-spacing: -0.5px;
        """)

        # Description
        description = QLabel(
            "Want to explore the code or contribute? Check out the project on GitHub. "
            "Feel free to open issues or submit pull requests. "
            "Your feedback and contributions are welcome."
        )
        description.setStyleSheet("""
            font-size: 15px; 
            color: #bbb; 
            background: none; 
            border: none;
            line-height: 24px;
        """)
        description.setWordWrap(True)

        # Subtle GitHub button - minimal and clean
        github_btn = QPushButton("View on GitHub →")
        github_btn.setCursor(QCursor(Qt.PointingHandCursor))
        github_btn.setFixedHeight(50)
        github_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.05);
                color: #ccc;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                padding: 12px 20px;
                font-size: 15px;
                font-weight: 500;
                text-align: left;
                padding-left: 20px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.08);
                border: 1px solid rgba(255, 255, 255, 0.15);
                color: white;
            }
            QPushButton:pressed {
                background: rgba(255, 255, 255, 0.03);
            }
        """)
        github_btn.clicked.connect(lambda: QDesktopServices.openUrl(
            QUrl("https://github.com/TRX-1000/Weatherly-v2")
        ))

        about_layout.addWidget(app_name)
        about_layout.addWidget(description)
        about_layout.addSpacing(5)
        about_layout.addWidget(github_btn)

        layout.addWidget(about_frame)
        layout.addSpacing(20)

        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)

    def create_setting_card(self, title, description, options, setting_key):
        """Create a settings card with radio buttons"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: #1a1a1a;
                border: 1px solid #2a2a2a;
                border-radius: 20px;
            }
        """)
        card.setMinimumHeight(280)
        
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(25, 25, 25, 25)
        card_layout.setSpacing(15)
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            font-size: 24px; 
            font-weight: 600; 
            color: white;
            border: none;
            letter-spacing: -0.3px;
            background: none;
        """)
        
        # Description
        desc_label = QLabel(description)
        desc_label.setStyleSheet("""
            font-size: 16px;
            color: #888;
            border: none;
            background: none;
            margin-bottom: 5px;
        """)
        desc_label.setWordWrap(True)
        
        card_layout.addWidget(title_label)
        card_layout.addWidget(desc_label)
        
        # Options
        button_group = QButtonGroup(card)
        
        for i, (label, value) in enumerate(options):
            option_container = QFrame()
            option_container.setStyleSheet("""
                QFrame {
                    background: transparent;
                    border-radius: 10px;
                    border: none;
                }
            """)
            
            option_layout = QHBoxLayout(option_container)
            option_layout.setContentsMargins(12, 10, 12, 10)
            
            radio = QRadioButton(label)
            radio.setStyleSheet("""
                QRadioButton {
                    color: white;
                    font-size: 16px;
                    background: transparent;
                    spacing: 12px;
                    font-weight: 500;
                }
                QRadioButton::indicator {
                    width: 20px;
                    height: 20px;
                    border-radius: 10px;
                    border: 2px solid #555;
                    background-color: #1a1a1a;
                }
                QRadioButton::indicator:checked {
                    background: #4a8fff;
                    border-color: #5ba3ff;
                }
                QRadioButton::indicator:hover {
                    border-color: #777;
                }
            """)
            
            if self.settings.get(setting_key) == value:
                radio.setChecked(True)
            
            radio.toggled.connect(lambda checked, k=setting_key, v=value: 
                                 self.update_setting_and_apply(k, v) if checked else None)
            
            button_group.addButton(radio)
            option_layout.addWidget(radio)
            option_layout.addStretch()
            
            card_layout.addWidget(option_container)
        
        card_layout.addStretch()
        return card
    
    def create_text_input_card(self, title, description, setting_key):
        """Create a settings card with text input"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: #1a1a1a;
                border: 1px solid #2a2a2a;
                border-radius: 20px;
            }
        """)
        
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(25, 25, 25, 25)
        card_layout.setSpacing(15)
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            font-size: 24px; 
            font-weight: 600; 
            border: none;
            color: white;
            letter-spacing: -0.3px;
            background: none;
        """)
        
        # Description
        desc_label = QLabel(description)
        desc_label.setStyleSheet("""
            font-size: 16px;
            color: #888;
            border: none;
            background: none;
            margin-bottom: 10px;
        """)
        desc_label.setWordWrap(True)
        
        card_layout.addWidget(title_label)
        card_layout.addWidget(desc_label)
        
        # Text input
        text_input = QLineEdit()
        text_input.setPlaceholderText("Enter city name (e.g., London, Tokyo)")
        text_input.setText(self.settings.get(setting_key, ""))
        text_input.setStyleSheet("""
            QLineEdit {
                background: #262626;
                border: 2px solid #333;
                border-radius: 12px;
                padding: 15px;
                color: white;
                font-size: 16px;
                font-weight: 500;
            }
            QLineEdit:focus {
                border: 2px solid #5ba3ff;
                background: #2a2a2a;
            }
            QLineEdit::placeholder {
                color: #666;
            }
        """)
        text_input.textChanged.connect(lambda text, k=setting_key: self.update_setting_and_apply(k, text))
        
        card_layout.addWidget(text_input)
        card_layout.addStretch()
        
        return card
    
    def clear_all_cities(self):
        """Clear all saved cities from sidebar with styled confirmation dialog"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
        
        # Create custom dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Clear All Cities")
        dialog.setModal(True)
        dialog.setFixedSize(450, 200)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #1a1a1a;
                border-radius: 16px;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("Clear All Saved Cities?")
        title.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            background: none;
            color: white;
        """)
        
        # Message
        message = QLabel("This action cannot be undone. All saved cities will be permanently removed.")
        message.setStyleSheet("""
            font-size: 14px;
            color: #bbb;
            background: none;
            line-height: 20px;
        """)
        message.setWordWrap(True)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedHeight(45)
        cancel_btn.setCursor(QCursor(Qt.PointingHandCursor))
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: #262626;
                color: white;
                border: 1px solid #3a3a3a;
                border-radius: 10px;
                font-size: 15px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #2e2e2e;
                border: 1px solid #444;
            }
            QPushButton:pressed {
                background: #222;
            }
        """)
        cancel_btn.clicked.connect(dialog.reject)
        
        clear_btn = QPushButton("Clear All")
        clear_btn.setFixedHeight(45)
        clear_btn.setCursor(QCursor(Qt.PointingHandCursor))
        clear_btn.setStyleSheet("""
            QPushButton {
                background: #ff6b6b;
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 15px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #ff7b7b;
            }
            QPushButton:pressed {
                background: #ee5b5b;
            }
        """)
        clear_btn.clicked.connect(dialog.accept)
        
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(clear_btn)
        
        layout.addWidget(title)
        layout.addWidget(message)
        layout.addStretch()
        layout.addLayout(button_layout)
        
        # Show dialog and proceed only if accepted
        if dialog.exec_() != QDialog.Accepted:
            return
        
        # If user clicked "Clear All", proceed with clearing
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
    
        # Clear info cards
        self.feels_like_card.value_label.setText("--°C")
        self.humidity_card.value_label.setText("--%")
        self.wind_card.value_label.setText("-- m/s")
        self.pressure_card.value_label.setText("-- hPa")
        self.clouds_card.value_label.setText("--%")
        self.visibility_card.value_label.setText("-- km")
        self.precip_card.value_label.setText("-- mm")
        self.sunrise_card.value_label.setText("--:--")
        self.sunset_card.value_label.setText("--:--")
        
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
    
    def create_section(self, parent_layout, title, description, options, setting_key):
        """Create a settings section with radio buttons"""
        section_container = QFrame()
        section_container.setStyleSheet("background: transparent;")
        
        container_layout = QVBoxLayout(section_container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(12)
        
        # Title
        section_label = QLabel(title)
        section_label.setStyleSheet("""
            font-size: 22px; 
            font-weight: 600; 
            border: none;
            color: white;
            letter-spacing: -0.3px;
        """)
        
        # Description
        desc_label = QLabel(description)
        desc_label.setStyleSheet("""
            font-size: 14px;
            color: #888;
            border: none;
            margin-bottom: 8px;
        """)
        
        container_layout.addWidget(section_label)
        container_layout.addWidget(desc_label)
        
        # Options frame  
        section_frame = QFrame()
        section_frame.setStyleSheet("""
            QFrame {
                background: #1a1a1a;
                border: 1px solid #2a2a2a;
                border-radius: 18px;
                padding: 8px;
            }
        """)
        
        section_layout = QVBoxLayout(section_frame)
        section_layout.setSpacing(8)
        section_layout.setContentsMargins(8, 8, 8, 8)
        
        button_group = QButtonGroup(self)
        
        for i, (label, value) in enumerate(options):
            # Create option container for hover effect
            option_container = QFrame()
            option_container.setStyleSheet("""
                QFrame {
                    background: transparent;
                    border-radius: 12px;
                    border: none;
                }
               
            """)
            
            option_layout = QHBoxLayout(option_container)
            option_layout.setContentsMargins(15, 12, 15, 12)
            
            radio = QRadioButton(label)
            radio.setStyleSheet("""
                QRadioButton {
                    color: white;
                    font-size: 16px;
                    background: transparent;
                    border: none;
                    spacing: 15px;
                    font-weight: 500;
                }
                QRadioButton::indicator {
                    width: 24px;
                    height: 24px;
                    border-radius: 12px;
                    border: 2px solid #555;
                    background-color: #1a1a1a;
                }
                QRadioButton::indicator:checked {
                    background: #4a8fff;
                    border-color: #5ba3ff;
                }

            """)
            
            if self.settings.get(setting_key) == value:
                radio.setChecked(True)
            
            radio.toggled.connect(lambda checked, k=setting_key, v=value: 
                                 self.update_setting(k, v) if checked else None)
            
            button_group.addButton(radio)
            option_layout.addWidget(radio)
            option_layout.addStretch()
            
            section_layout.addWidget(option_container)
        
        container_layout.addWidget(section_frame)
        parent_layout.addWidget(section_container)
    
    def update_setting(self, key, value):
        """Update a setting value"""
        self.settings[key] = value
    
    def update_setting_and_apply(self, key, value):
        """Update a setting value and immediately apply it"""
        self.settings[key] = value
        self.settings_changed.emit(self.settings)

    def save_settings(self):
        """Save settings and emit signal"""
        self.settings_changed.emit(self.settings)
        self.back_clicked.emit()

    def get_settings(self):
        """Return current settings"""
        return self.settings
    
    def on_back_clicked(self):
        """Handle back/done button click"""
        # Emit one final settings_changed to ensure everything is saved
        self.settings_changed.emit(self.settings)
        self.back_clicked.emit()