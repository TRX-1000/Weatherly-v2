from PyQt5.QtWidgets import QFrame, QLabel, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt

class WeatherCard(QFrame):
    def __init__(self, city, temp=None, cond=None, hi=None, lo=None):
        super().__init__()

        self.city = city

        self.setStyleSheet("""
            QFrame {
                background-color: #262626;
                border-radius: 15px;
            }
            QLabel {
                color: white;
            }
        """)

        self.setFixedHeight(90)

        # --- Layouts ---
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(5)

        # Row 1: city + temp
        self.row1 = QHBoxLayout()
        self.city_label = QLabel(self.city)
        self.city_label.setStyleSheet("font-size: 18px; font-weight: bold;")

        self.temp_label = QLabel(temp or "--°C")
        self.temp_label.setStyleSheet("font-size: 22px; font-weight: bold;")

        self.row1.addWidget(self.city_label)
        self.row1.addStretch()
        self.row1.addWidget(self.temp_label)

        # Row 2: condition + hi/lo
        self.row2 = QHBoxLayout()
        self.cond_label = QLabel(cond or "Loading…")
        self.cond_label.setStyleSheet("font-size: 14px; color: #ccc;")

        hilo_text = f"H:{hi}  L:{lo}" if hi and lo else "H:--  L:--"
        self.hilo_label = QLabel(hilo_text)
        self.hilo_label.setStyleSheet("font-size: 14px; color: #aaa;")

        self.row2.addWidget(self.cond_label)
        self.row2.addStretch()
        self.row2.addWidget(self.hilo_label)

        layout.addLayout(self.row1)
        layout.addLayout(self.row2)

    # --------------------------------------------------------
    # PUBLIC METHOD: allow MainWindow to update card live
    # --------------------------------------------------------
    def update_weather(self, temp, cond, hi, lo):
        self.temp_label.setText(f"{temp}°C")
        self.cond_label.setText(cond)
        self.hilo_label.setText(f"H:{hi}  L:{lo}")
