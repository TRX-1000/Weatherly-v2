from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QFrame, QRadioButton, QButtonGroup, QScrollArea
)
from PyQt5.QtCore import Qt, pyqtSignal, QUrl
from PyQt5.QtGui import QDesktopServices, QCursor


class SettingsPage(QWidget):
    settings_changed = pyqtSignal(dict)
    back_clicked = pyqtSignal()
    
    def __init__(self, parent=None, current_settings=None):
        super().__init__(parent)
        
        # Load current settings or use defaults
        self.settings = current_settings or {
            "temperature_unit": "celsius",
            "wind_unit": "metric",
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
        layout.addWidget(prefs_header)
        
        # Temperature Unit Section
        self.create_section(
            layout,
            "🌡️  Temperature Unit",
            "Choose your preferred temperature scale",
            [("Celsius (°C)", "celsius"), ("Fahrenheit (°F)", "fahrenheit")],
            "temperature_unit"
        )
        
        # Wind Speed Unit Section
        self.create_section(
            layout,
            "💨  Wind Speed Unit",
            "Choose your preferred wind speed measurement",
            [("Meters per second (m/s)", "metric"), ("Miles per hour (mph)", "imperial")],
            "wind_unit"
        )
        
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

        save_btn = QPushButton("💾  Save Settings")
        save_btn.setCursor(QCursor(Qt.PointingHandCursor))
        save_btn.setFixedSize(300, 45)
        save_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4a8fff, stop:0.5 #5ba3ff, stop:1 #6db5ff);
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 18px;
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
        save_btn.clicked.connect(self.save_settings)
        

        layout.addWidget(save_btn)

        
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
        
        layout.addStretch()
        
        
        
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)
    
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
            color: white;
            letter-spacing: -0.3px;
        """)
        
        # Description
        desc_label = QLabel(description)
        desc_label.setStyleSheet("""
            font-size: 14px;
            color: #888;
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
                QRadioButton::indicator:hover {
                    border-color: #777;
                }
                QRadioButton::indicator:checked:hover {
                    border-color: #6db5ff;
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
    
    def save_settings(self):
        """Save settings and emit signal"""
        self.settings_changed.emit(self.settings)
        self.back_clicked.emit()
    
    def on_back_clicked(self):
        """Handle back button click"""
        self.back_clicked.emit()
    
    def get_settings(self):
        """Return current settings"""
        return self.settings