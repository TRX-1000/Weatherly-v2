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
            "default_city": "",
            "news-count": 10,
            "auto_refresh": True
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
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1a1a1a, stop:1 #1f1f1f);
                border-bottom: 1px solid #2a2a2a;
            }
        """)
        top_bar.setFixedHeight(80)
        
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(30, 20, 30, 20)
        
        back_btn = QPushButton("← Back")
        back_btn.setCursor(QCursor(Qt.PointingHandCursor))
        back_btn.setFixedSize(120, 45)
        back_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2d2d2d, stop:1 #262626);
                color: white;
                border: 1px solid #3a3a3a;
                border-radius: 12px;
                font-size: 16px;
                font-weight: 600;
                padding: 0 20px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #353535, stop:1 #2e2e2e);
                border: 1px solid #444;
            }
            QPushButton:pressed {
                background: #222;
            }
        """)
        back_btn.clicked.connect(self.on_back_clicked)
        
        # Settings title in top bar
        settings_title = QLabel("⚙️  Settings")
        settings_title.setStyleSheet("""
            font-size: 26px; 
            font-weight: bold; 
            color: white;
            border: none;
            background: none;
            padding-left: 20px;
        """)
        
        top_layout.addWidget(back_btn)
        top_layout.addWidget(settings_title)
        top_layout.addStretch()
        
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
            QScrollBar::handle:vertical {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3a3a3a, stop:1 #444);
                border-radius: 6px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #454545, stop:1 #4a4a4a);
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: #111;")
        
        layout = QVBoxLayout(scroll_content)
        layout.setContentsMargins(50, 40, 50, 50)
        layout.setSpacing(35)
        
        # Top row with header and Done button
        top_row = QHBoxLayout()
        top_row.setSpacing(20)
        
        # Preferences Section Header
        prefs_header = QLabel("🎛️  Preferences")
        prefs_header.setStyleSheet("""
            font-size: 32px; 
            font-weight: bold; 
            color: white;
            border: none;
            margin-bottom: 10px;
            letter-spacing: -0.5px;
        """)
        
        top_row.addWidget(prefs_header)
        top_row.addStretch()
        
        # Done button at top right
        done_btn = QPushButton("✓  Done")
        done_btn.setCursor(QCursor(Qt.PointingHandCursor))
        done_btn.setFixedSize(140, 50)
        done_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4a8fff, stop:0.5 #5ba3ff, stop:1 #6db5ff);
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 17px;
                font-weight: 700;
                letter-spacing: 0.5px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5b9fff, stop:0.5 #6cb3ff, stop:1 #7dc5ff);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3978ee, stop:0.5 #4a92ee, stop:1 #5ca4ee);
            }
        """)
        done_btn.clicked.connect(self.on_back_clicked)
        
        top_row.addWidget(done_btn)
        layout.addLayout(top_row)
        
        # Grid container for settings cards
        grid_container = QWidget()
        grid_container.setStyleSheet("background: transparent;")
        grid_layout = QGridLayout(grid_container)
        grid_layout.setSpacing(20)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        
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
            [("Meters per second (m/s)", "metric"), ("Miles per hour (mph)", "imperial")],
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
        
        # Add cards to grid (2 columns)
        grid_layout.addWidget(self.temp_card, 0, 0)
        grid_layout.addWidget(self.wind_card, 0, 1)
        grid_layout.addWidget(self.news_card, 1, 0)
        grid_layout.addWidget(self.default_city_card, 1, 1)
        
        layout.addWidget(grid_container)
        
        layout.addSpacing(20)
        
        # Decorative divider
        divider_container = QFrame()
        divider_container.setStyleSheet("background: transparent;")
        divider_layout = QHBoxLayout(divider_container)
        divider_layout.setContentsMargins(0, 20, 0, 20)
        
        left_line = QFrame()
        left_line.setFrameShape(QFrame.HLine)
        left_line.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 transparent, stop:1 #333); max-height: 1px;")
        
        divider_icon = QLabel("✦")
        divider_icon.setStyleSheet("color: #555; font-size: 14px; padding: 0 15px;")
        
        right_line = QFrame()
        right_line.setFrameShape(QFrame.HLine)
        right_line.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #333, stop:1 transparent); max-height: 1px;")
        
        divider_layout.addWidget(left_line)
        divider_layout.addWidget(divider_icon)
        divider_layout.addWidget(right_line)

        
        layout.addWidget(divider_container)
        
        # About Section
        about_label = QLabel("ℹ️  About Weatherly")
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
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1e1e1e, stop:1 #1a1a1a);
                border: none;
                padding: 30px;
            }
        """)
        about_layout = QVBoxLayout(about_frame)
        about_layout.setSpacing(18)
        
        app_name = QLabel("Weatherly v2.0")
        app_name.setStyleSheet("""
            font-size: 28px; 
            font-weight: bold; 
            color: white; 
            background: none;
            letter-spacing: -0.5px;
        """)
        
        description = QLabel("Want to contribute explore the code or contribute? Check out the project on GitHub! Feel free to open issues or submit pull requests. Your feedback and contributions are welcome!")
        description.setStyleSheet("""
            font-size: 15px; 
            color: #bbb; 
            background: none; 
            border: none;
            line-height: 24px;
        """)
        description.setWordWrap(True)
        
        github_btn = QPushButton("🔗 View on GitHub")
        github_btn.setCursor(QCursor(Qt.PointingHandCursor))
        github_btn.setFixedHeight(55)
        github_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2d2d2d, stop:1 #262626);
                color: white;
                border: 1px solid #3a3a3a;
                border-radius: 14px;
                padding: 12px 20px;
                font-size: 20px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #353535, stop:1 #2e2e2e);
                border: 1px solid #444;
            }
            QPushButton:pressed {
                background: #222;
            }
        """)
        github_btn.clicked.connect(lambda: QDesktopServices.openUrl(
            QUrl("https://github.com/TRX-1000/Weatherly-v2")
        ))
        
        about_layout.addWidget(app_name)
        about_layout.addWidget(description)

        about_layout.addWidget(github_btn)
        
        layout.addWidget(about_frame)
        
        layout.addSpacing(20)
        
        # Data Management Section
        data_header = QLabel("🗂️ Data Management")
        data_header.setStyleSheet("""
            font-size: 32px; 
            font-weight: bold; 
            color: white;
            border: none;
            margin-top: 10px;
            margin-bottom: 10px;
            letter-spacing: -0.5px;
        """)
        layout.addWidget(data_header)
        
        # Clear Cities Button
        clear_cities_btn = QPushButton("🗑️  Clear All Saved Cities")
        clear_cities_btn.setCursor(QCursor(Qt.PointingHandCursor))
        clear_cities_btn.setFixedHeight(60)
        clear_cities_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #d64545, stop:0.5 #e85555, stop:1 #ff6565);
                color: white;
                border: none;
                border-radius: 16px;
                font-size: 18px;
                font-weight: 700;
                letter-spacing: 0.5px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #e05555, stop:0.5 #f26565, stop:1 #ff7575);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #c53535, stop:0.5 #d74545, stop:1 #ee5555);
            }
        """)
        clear_cities_btn.clicked.connect(self.clear_all_cities)
        
        layout.addWidget(clear_cities_btn)
        
        layout.addStretch()
        
        
        
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)

    def create_setting_card(self, title, description, options, setting_key):
        """Create a settings card with radio buttons"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1e1e1e, stop:1 #1a1a1a);
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
            font-size: 20px; 
            font-weight: 600; 
            color: white;
            border: none;
            letter-spacing: -0.3px;
            background: none;
        """)
        
        # Description
        desc_label = QLabel(description)
        desc_label.setStyleSheet("""
            font-size: 13px;
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
                    font-size: 15px;
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
                    background: qradialgradient(cx:0.5, cy:0.5, radius:0.5,
                        fx:0.5, fy:0.5, stop:0 #6db5ff, stop:0.6 #5ba3ff, stop:1 #4a8fff);
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
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1e1e1e, stop:1 #1a1a1a);
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
            font-size: 20px; 
            font-weight: 600; 
            border: none;
            color: white;
            letter-spacing: -0.3px;
            background: none;
        """)
        
        # Description
        desc_label = QLabel(description)
        desc_label.setStyleSheet("""
            font-size: 13px;
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
                font-size: 15px;
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
        """Show confirmation dialog and clear all cities"""
        reply = QMessageBox.question(
            self,
            "Clear All Cities",
            "Are you sure you want to clear all saved cities?\n\nThis action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.clear_cities_requested.emit()
            
            # Show success message
            success_msg = QMessageBox(self)
            success_msg.setIcon(QMessageBox.Information)
            success_msg.setWindowTitle("Cities Cleared")
            success_msg.setText("All saved cities have been cleared successfully.")
            success_msg.setStyleSheet("""
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
                QPushButton:hover {
                    background-color: #6db5ff;
                }
            """)
            success_msg.exec_()
    
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
        
        # Options frame with gradient
        section_frame = QFrame()
        section_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1e1e1e, stop:1 #1a1a1a);
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
                    background: qradialgradient(cx:0.5, cy:0.5, radius:0.5,
                        fx:0.5, fy:0.5, stop:0 #6db5ff, stop:0.6 #5ba3ff, stop:1 #4a8fff);
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
    
    def on_back_clicked(self):
        """Handle back button click"""
        # Emit one final settings_changed to ensure everything is saved
        self.settings_changed.emit(self.settings)
        self.back_clicked.emit()

    def get_settings(self):
        """Return current settings"""
        return self.settings