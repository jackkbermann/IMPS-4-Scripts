from camera_gui import *
from camera_funcs import *
from PyQt5.QtWidgets import QApplication, QMainWindow
import sys
import threading

def setup_connections(self):
    self.stop_event = threading.Event()
    self.ui.stop_live_view_button.clicked.connect(self.stop_live_view)
    self.ui.start_live_view_button.clicked.connect(self.start_live_view)

def start_live_view(self):
    self.stop_event.clear()
    threading.Thread(target=live_view, args=(self.ui.live_view_label,), daemon=True).start()

def stop_live_view(self)
    self.stop_event.set()
    
def main():
    stop_event = threading.Event()
    app = QApplication(sys.argv)
    window = CameraTabsWidget()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()