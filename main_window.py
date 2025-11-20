from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
    QFrame, QLineEdit
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve

from ui.sidebar_card import WeatherCard
from ui.mock_data import MOCK_WEATHER


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Weatherly")
        self.setMinimumSize(1200, 700)

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

        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setContentsMargins(12, 12, 12, 12)
        self.sidebar_layout.setSpacing(12)

        self.load_mock_cards()
        self.sidebar_layout.addStretch()

        # ---------------- RIGHT PANEL ----------------
        self.right = QFrame()
        self.right.setStyleSheet("background-color: #111;")

        right_layout = QVBoxLayout(self.right)
        right_layout.setContentsMargins(20, 20, 20, 20)
        right_layout.setSpacing(15)

        top_bar = QHBoxLayout()
        top_bar.setSpacing(12)

        # Menu Button
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

        # Search
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search for a place...")
        self.search_bar.setFixedHeight(45)
        self.search_bar.setStyleSheet("""
            QLineEdit {
                background: #262626;
                border-radius: 22px;
                padding-left: 20px;
                color: white;
                font-size: 16px;
            }
        """)

        # Refresh
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

        top_bar.addWidget(self.menu_button)
        top_bar.addWidget(self.search_bar)
        top_bar.addWidget(self.refresh_button)

        right_layout.addLayout(top_bar)

        content = QFrame()
        content.setStyleSheet("background: #181818; border-radius: 14px;")
        right_layout.addWidget(content)

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

    # ---------------- Load Cards ----------------
    def load_mock_cards(self):
        for data in MOCK_WEATHER:
            card = WeatherCard(
                data["city"],
                data["temp"],
                data["condition"],
                data["hi"],
                data["lo"]
            )
            self.sidebar_layout.addWidget(card)

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
