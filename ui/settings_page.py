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
        
        self.setStyleSheet("background: transparent;")
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Top bar with back button
        top_bar = QFrame()
        top_bar.setStyleSheet("background: transparent;")
        top_bar.setFixedHeight(65)
        
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(0, 0, 0, 15)
        
        back_btn = QPushButton("← Back")
        back_btn.setCursor(QCursor(Qt.PointingHandCursor))
        back_btn.setFixedSize(100, 45)
        back_btn.setStyleSheet("""
            QPushButton {
                background: #262626;
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 16px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #333;
            }
        """)
        back_btn.clicked.connect(self.on_back_clicked)
        
        top_layout.addWidget(back_btn)
        top_layout.addStretch()
        
        main_layout.addWidget(top_bar)
        
        # Scrollable content area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
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
        
        layout = QVBoxLayout(scroll_content)
        layout.setContentsMargins(35, 20, 35, 35)
        layout.setSpacing(30)
        
        # Title
        title = QLabel("⚙️ Settings")
        title.setStyleSheet("font-size: 36px; font-weight: bold; color: white; background: transparent;")
        layout.addWidget(title)
        
        # Temperature Unit Section
        self.create_section(
            layout,
            "🌡️ Temperature Unit",
            [("Celsius (°C)", "celsius"), ("Fahrenheit (°F)", "fahrenheit")],
            "temperature_unit"
        )
        
        # Wind Speed Unit Section
        self.create_section(
            layout,
            "💨 Wind Speed Unit",
            [("Meters/second (m/s)", "metric"), ("Miles/hour (mph)", "imperial")],
            "wind_unit"
        )
        
        # Divider
        divider = QFrame()
        divider.setStyleSheet("background-color: #333; max-height: 1px;")
        divider.setFrameShape(QFrame.HLine)
        layout.addWidget(divider)
        
        # About Section
        about_label = QLabel("ℹ️ About")
        about_label.setStyleSheet("font-size: 26px; font-weight: bold; color: white; margin-top: 10px; background: transparent;")
        layout.addWidget(about_label)
        
        about_frame = QFrame()
        about_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(38, 38, 38, 0.6);
                border-radius: 16px;
                padding: 25px;
            }
        """)
        about_layout = QVBoxLayout(about_frame)
        about_layout.setSpacing(15)
        
        app_name = QLabel("Weatherly v2.0")
        app_name.setStyleSheet("font-size: 22px; font-weight: bold; color: white; background: none;")
        
        description = QLabel("A modern weather application with beautiful UI and smooth animations.")
        description.setStyleSheet("font-size: 15px; color: #bbb; background: none; line-height: 1.5;")
        description.setWordWrap(True)
        
        github_btn = QPushButton("🔗 View on GitHub")
        github_btn.setCursor(QCursor(Qt.PointingHandCursor))
        github_btn.setFixedHeight(50)
        github_btn.setStyleSheet("""
            QPushButton {
                background-color: #333;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 12px 20px;
                font-size: 15px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #404040;
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
        
        # Save button at bottom
        save_btn = QPushButton("💾 Save Settings")
        save_btn.setCursor(QCursor(Qt.PointingHandCursor))
        save_btn.setFixedHeight(55)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #5ba3ff;
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 17px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #4a92ee;
            }
        """)
        save_btn.clicked.connect(self.save_settings)
        
        layout.addWidget(save_btn)
        
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)
    
    def create_section(self, parent_layout, title, options, setting_key):
        """Create a settings section with radio buttons"""
        section_label = QLabel(title)
        section_label.setStyleSheet("font-size: 24px; font-weight: bold; color: white; background: transparent;")
        parent_layout.addWidget(section_label)
        
        section_frame = QFrame()
        section_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(38, 38, 38, 0.6);
                border-radius: 16px;
                padding: 20px;
            }
        """)
        
        section_layout = QVBoxLayout(section_frame)
        section_layout.setSpacing(15)
        
        button_group = QButtonGroup(self)
        
        for label, value in options:
            radio = QRadioButton(label)
            radio.setStyleSheet("""
                QRadioButton {
                    color: white;
                    font-size: 16px;
                    background: transparent;
                    spacing: 12px;
                    padding: 10px;
                }
                QRadioButton::indicator {
                    width: 22px;
                    height: 22px;
                    border-radius: 11px;
                    border: 2px solid #666;
                    background-color: #1a1a1a;
                }
                QRadioButton::indicator:checked {
                    background-color: #5ba3ff;
                    border-color: #5ba3ff;
                }
                QRadioButton::indicator:hover {
                    border-color: #888;
                }
            """)
            
            if self.settings.get(setting_key) == value:
                radio.setChecked(True)
            
            radio.toggled.connect(lambda checked, k=setting_key, v=value: 
                                 self.update_setting(k, v) if checked else None)
            
            button_group.addButton(radio)
            section_layout.addWidget(radio)
        
        parent_layout.addWidget(section_frame)
    
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