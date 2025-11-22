from PyQt5.QtWidgets import QFrame, QLabel, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QDesktopServices, QCursor


class NewsCard(QFrame):
    def __init__(self, title, source, published, summary, link):
        super().__init__()
        
        self.link = link
        
        self.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #262626, stop:1 #1e1e1e);
                border-radius: 16px;
                border: 1px solid #333;
            }
            QFrame:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2d2d2d, stop:1 #252525);
                border: 1px solid #444;
            }
        """)
        
        self.setCursor(QCursor(Qt.PointingHandCursor))
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 20, 25, 20)
        layout.setSpacing(10)
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 17px; font-weight: bold; color: white; line-height: 1.4;")
        title_label.setWordWrap(True)
        
        # Source and date
        meta_layout = QHBoxLayout()
        meta_layout.setSpacing(15)
        
        source_label = QLabel(f"📌 {source}")
        source_label.setStyleSheet("font-size: 13px; color: #999;")
        
        date_label = QLabel(published.split(',')[0] if ',' in published else published[:20])
        date_label.setStyleSheet("font-size: 13px; color: #777;")
        
        meta_layout.addWidget(source_label)
        meta_layout.addStretch()
        meta_layout.addWidget(date_label)
        
        # Summary (truncated)
        summary_text = summary[:180] + "..." if len(summary) > 180 else summary
        summary_label = QLabel(summary_text)
        summary_label.setStyleSheet("font-size: 14px; color: #bbb; line-height: 1.5;")
        summary_label.setWordWrap(True)
        
        # Read more link
        read_more = QLabel("Read full article →")
        read_more.setStyleSheet("font-size: 14px; color: #5ba3ff; font-weight: 600; margin-top: 5px;")
        
        layout.addWidget(title_label)
        layout.addLayout(meta_layout)
        layout.addWidget(summary_label)
        layout.addWidget(read_more)
    
    def mousePressEvent(self, event):
        """Open link in browser when clicked"""
        QDesktopServices.openUrl(QUrl(self.link))
        super().mousePressEvent(event)