from camera_gui import *
from camera_funcs import *
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget, QMessageBox
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
import sys
import threading


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #001f3f;")
        self.setWindowTitle("IMPS4 Camera Control")
        self.resize(1000, 800)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.welcome_screen = WelcomeScreen()
        self.camera_ui = CameraTabsWidget()

        self.stack.addWidget(self.welcome_screen)
        self.stack.addWidget(self.camera_ui)

        self.stop_event = threading.Event()
        self.live_view_thread = None  
        self.capture_thread = None    

        self.welcome_screen.continue_button.clicked.connect(self.go_to_camera_ui)

        # Setup after transition
        self.setup_done = False

    def go_to_camera_ui(self):
        name = self.welcome_screen.name_input.text().strip()
        if not name:
            QMessageBox.critical(self, "Invalid Input", "Please enter a valid name.")
            return

        self.stack.setCurrentWidget(self.camera_ui)

        if not self.setup_done:
            self.setup_connections()
            self.setup_done = True


    def setup_connections(self):
        self.camera_ui.stop_live_view_button.clicked.connect(self.stop_live_view)
        self.camera_ui.start_live_view_button.clicked.connect(self.start_live_view)
        self.camera_ui.start_capture_button.clicked.connect(self.start_capture)

    def start_live_view(self):
        self.stop_event.clear()
        exposure_time = self.camera_ui.get_live_exposure_time()
        if exposure_time is None:
            return
        self.live_view_thread = threading.Thread(
            target=live_view,
            args=(self.camera_ui.live_view_label, self.stop_event, exposure_time),
            daemon=True)
        self.live_view_thread.start()
    
    def stop_live_view(self):
        self.stop_event.set()

    def start_capture(self):
        exposure_time = self.camera_ui.get_exposure_time()
        num_frames = self.camera_ui.get_num_frames()
        average = self.camera_ui.get_average_bool()
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
