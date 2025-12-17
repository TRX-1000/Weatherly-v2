from PyQt5.QtWidgets import QFrame, QLabel, QVBoxLayout, QHBoxLayout


def capitalize_city_name(city_name):
    if not city_name:
        return city_name
    
    words = city_name.split()
    capitalized_words = [word.capitalize() for word in words]
    return ' '.join(capitalized_words)


class WeatherCard(QFrame):
    
    def __init__(self, city, temp=None, cond=None, hi=None, lo=None):
        super().__init__()

        # Store the city name
        self.city = city

        # Card styling with hover effect
        self.setStyleSheet("""
            QFrame {
                background-color: #262626;
                border-radius: 15px;
            }
            QFrame:hover {
                background-color: #2d2d2d;
            }
            QLabel {
                color: white;
            }
        """)

        self.setFixedHeight(90)

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(5)

        # Row 1: City name + Current temperature
        self.row1 = QHBoxLayout()
        
        # City label with proper capitalization
        self.city_label = QLabel(capitalize_city_name(self.city))
        self.city_label.setStyleSheet("font-size: 18px; font-weight: bold; background: none;")

        # Temperature label
        self.temp_label = QLabel(temp or "--°C")
        self.temp_label.setStyleSheet("font-size: 22px; font-weight: bold; background: none;")

        self.row1.addWidget(self.city_label)
        self.row1.addStretch()
        self.row1.addWidget(self.temp_label)

        # Row 2: Weather condition + High/Low temperatures
        self.row2 = QHBoxLayout()
        
        # Condition label
        self.cond_label = QLabel(cond or "Loading...")
        self.cond_label.setStyleSheet("font-size: 14px; color: #ccc; background: none;")

        # High/Low temperatures label
        hilo_text = f"H:{hi}  L:{lo}" if hi and lo else "H:--  L:--"
        self.hilo_label = QLabel(hilo_text)
        self.hilo_label.setStyleSheet("font-size: 14px; color: #aaa; background: none;")

        self.row2.addWidget(self.cond_label)
        self.row2.addStretch()
        self.row2.addWidget(self.hilo_label)

        # Add both rows to main layout
        layout.addLayout(self.row1)
        layout.addLayout(self.row2)

    def update_weather(self, temp, cond, hi, lo):
        self.temp_label.setText(temp)
        self.cond_label.setText(cond)
        self.hilo_label.setText(f"H: {hi}  L: {lo}")