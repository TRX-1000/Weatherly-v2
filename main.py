from PyQt5.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
    QFrame, QLineEdit
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve
import sys


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Weatherly")
        self.setMinimumSize(1200, 700)

        # ----- CONFIG -----
        self.sidebar_collapsed = 0
        self.sidebar_expanded = 250
        self.current_sidebar_width = self.sidebar_collapsed

        # MAIN LAYOUT
        self.root = QHBoxLayout(self)
        self.root.setContentsMargins(0, 0, 0, 0)
        self.root.setSpacing(0)

        # ------------------------------------------------------------------
        # SIDEBAR
        # ------------------------------------------------------------------
        self.sidebar = QFrame()
        self.sidebar.setStyleSheet("""
            background-color: #1a1a1a;
            border-right: 1px solid #333;
        """)
        self.sidebar.setFixedWidth(self.sidebar_collapsed)

        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(10, 10, 10, 10)
        sidebar_layout.setSpacing(15)

        sidebar_layout.addStretch()

        # ------------------------------------------------------------------
        # RIGHT CONTAINER
        # ------------------------------------------------------------------
        self.right = QFrame()
        self.right.setStyleSheet("background-color: #111;")

        right_layout = QVBoxLayout(self.right)
        right_layout.setContentsMargins(20, 20, 20, 20)
        right_layout.setSpacing(15)

        # ------------------ TOP BAR ------------------
        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(10, 0, 0, 0)
        top_bar.setSpacing(10)

        # Menu button (top left)
        self.menu_button = QPushButton("☰")
        self.menu_button.setFixedSize(45, 45)
        self.menu_button.setStyleSheet("""
            QPushButton {
                font-size: 24px;
                color: white;
                border: none;
                background: #262626;
                border-radius: 10px;
            }
            QPushButton:hover {
                background: #333;
            }
        """)
        self.menu_button.clicked.connect(self.toggle_sidebar)

        # Search bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("🔎 Search for a place. e.g., 'Texas' or 'London'")
        self.search_bar.setFixedHeight(45)
        self.search_bar.setStyleSheet("""
            QLineEdit {
                background-color: #262626;
                border-radius: 22px;
                padding-left: 20px;
                padding-right: 20px;
                font-size: 16px;
                color: white;
            }
            QLineEdit::placeholder {
                color: #777;
                font-size: 16px;
            }
        """)

        # Refresh button
        self.refresh_button = QPushButton("↻")
        self.refresh_button.setFixedSize(40, 40)
        self.refresh_button.setStyleSheet("""
            QPushButton {
                background: #262626;
                font-size: 24px;
                color: white;
                border-radius: 10px;
            }
            QPushButton:hover {
                background: #333;
            }
        """)
        self.refresh_button.clicked.connect(self.refresh_weather)

        top_bar.addWidget(self.menu_button)
        top_bar.addWidget(self.search_bar)
        top_bar.addWidget(self.refresh_button)

        right_layout.addLayout(top_bar)

        # Dummy content area
        filler = QFrame()
        filler.setStyleSheet("background: #181818; border-radius: 15px;")
        right_layout.addWidget(filler)

        # Add sidebar + right panel
        self.root.addWidget(self.sidebar)
        self.root.addWidget(self.right)

        # ------------------------------------------------------------------
        # ANIMATIONS
        # ------------------------------------------------------------------
        self.sidebar_anim = QPropertyAnimation(self.sidebar, b"minimumWidth")
        self.sidebar_anim.setEasingCurve(QEasingCurve.InOutCubic)
        self.sidebar_anim.setDuration(300)

        self.search_anim = QPropertyAnimation(self.search_bar, b"maximumWidth")
        self.search_anim.setEasingCurve(QEasingCurve.InOutCubic)
        self.search_anim.setDuration(300)

    # ==================================================================
    # SIDEBAR LOGIC
    # ==================================================================
    def toggle_sidebar(self):
        if self.current_sidebar_width == self.sidebar_collapsed:
            self.expand_sidebar()
        else:
            self.collapse_sidebar()

    def expand_sidebar(self):
        self.current_sidebar_width = self.sidebar_expanded

        diff = self.sidebar_expanded - self.sidebar_collapsed

        # Sidebar anim
        self.sidebar_anim.setStartValue(self.sidebar.width())
        self.sidebar_anim.setEndValue(self.sidebar_expanded)
        self.sidebar_anim.start()

        # Search bar shrink
        self.search_anim.setStartValue(self.search_bar.width())
        self.search_anim.setEndValue(max(150, self.search_bar.width() - diff))
        self.search_anim.start()

    def collapse_sidebar(self):
        self.current_sidebar_width = self.sidebar_collapsed

        diff = self.sidebar_expanded - self.sidebar_collapsed

        # Sidebar anim
        self.sidebar_anim.setStartValue(self.sidebar.width())
        self.sidebar_anim.setEndValue(self.sidebar_collapsed)
        self.sidebar_anim.start()

        # Search bar expand
        self.search_anim.setStartValue(self.search_bar.width())
        self.search_anim.setEndValue(self.search_bar.width() + diff)
        self.search_anim.start()

    def refresh_weather(self):
        print("Refreshing weather...")
        # Add your refresh logic here


# ----------------------------------------------------------------------

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())