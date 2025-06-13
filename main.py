from camera_gui import *
from camera_funcs import *
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
import sys
import threading


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = CameraTabsWidget()
        self.setCentralWidget(self.ui)
        self.stop_event = threading.Event()
        self.live_view_thread = None  
        self.capture_thread = None    
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
        self.live_view_thread = threading.Thread(
            target=live_view,
            args=(self.ui.live_view_label, self.stop_event, exposure_time),
            daemon=True)
        self.live_view_thread.start()
    
    def stop_live_view(self):
        self.stop_event.set()

    def start_capture(self):
        exposure_time = self.ui.get_exposure_time()
        num_frames = self.ui.get_num_frames()
        average = self.ui.get_average_bool()
        if exposure_time is None or num_frames is None:
            return
        self.capture_thread = threading.Thread(
            target=capture_image,
            args=(exposure_time, num_frames, average, "./output"),
            daemon=True)
        self.capture_thread.start()

def main():
    QtWidgets.QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QtWidgets.QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
