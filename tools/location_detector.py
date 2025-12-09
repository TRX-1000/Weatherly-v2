import geocoder
from PyQt5.QtCore import QThread, pyqtSignal


class LocationWorker(QThread):
    """Background thread for detecting location"""
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def run(self):
        try:
            # Get location using IP
            g = geocoder.ip('me')
            
            if g.ok and g.city:
                city = g.city
                self.finished.emit(city)
            else:
                self.error.emit("Could not detect location")
        except Exception as e:
            self.error.emit(f"Location detection failed: {str(e)}")