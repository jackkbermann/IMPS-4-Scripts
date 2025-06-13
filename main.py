from camera_gui import *
from camera_funcs import *
from PyQt5.QtWidgets import QApplication, QMainWindow
import sys
import threading

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = CameraTabsWidget()
        self.setCentralWidget(self.ui)
        self.stop_event = threading.Event()
        self.setup_connections()

    def setup_connections(self):
        self.ui.stop_live_view_button.clicked.connect(self.stop_live_view)
        self.ui.start_live_view_button.clicked.connect(self.start_live_view)
        self.ui.start_capture_button.clicked.connect(self.start_capture)

    def start_live_view(self):
        self.stop_event.clear()
        exposure_time = self.ui.get_live_exposure_time()
        if exposure_time is None:
            return
        threading.Thread(target=live_view, args=(self.ui.live_view_label, self.stop_event, exposure_time), daemon=True).start()
    
    def stop_live_view(self):
        self.stop_event.set()

    def start_capture(self):
        exposure_time = self.ui.get_exposure_time()
        if exposure_time is None:
            return
        threading.Thread(target=capture_image, args=(exposure_time, 1, False, "./output"), daemon=True).start()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
