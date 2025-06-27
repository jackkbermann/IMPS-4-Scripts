from camera_gui import *
from camera_funcs import *
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget, QMessageBox
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QThread
import sys
import threading
from datetime import date


def get_current_date():
    return date.today()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #001f3f;")
        self.setWindowTitle("IMPS4 Camera Control")
        self.resize(1000, 800)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.welcome_screen = WelcomeScreen()
        self.stack.addWidget(self.welcome_screen)

        self.stop_event = threading.Event()
        self.live_view_thread = None  
        self.capture_thread = None    

        self.setup_done = False

        # Connect the continue button to transition
        self.welcome_screen.continue_button.clicked.connect(self.go_to_camera_ui)

    def go_to_camera_ui(self):
        name = self.welcome_screen.name_input.text().strip()
        if not name:
            QMessageBox.critical(self, "Invalid Input", "Please enter a valid name.")
            return

        self.camera_ui = CameraTabsWidget(username=name)
        self.stack.addWidget(self.camera_ui)
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
        exposure_time_unit = self.camera_ui.get_live_exposure_unit()
        exposure_time = self.camera_ui.get_live_exposure_time(exposure_time_unit)
        if exposure_time is None:
            return
        if is_camera_connected() is False:
            QMessageBox.critical(
                self,
                "Camera Not Connected",
                "Please connect the camera before starting live view."
            )
            return

        self.live_thread = QThread()
        self.live_worker = LiveViewWorker(self.stop_event, exposure_time)
        self.live_worker.moveToThread(self.live_thread)

        self.live_worker.new_pixmap.connect(self.camera_ui.live_view_label.setPixmap)
        self.live_worker.finished.connect(self.live_thread.quit)
        self.live_worker.finished.connect(self.live_worker.deleteLater)
        self.live_thread.finished.connect(self.live_thread.deleteLater)

        self.live_thread.started.connect(self.live_worker.run(exposure_time))
        self.live_thread.start()
    
    def stop_live_view(self):
        self.stop_event.set()
        if self.live_thread and self.live_thread.isRunning():
            self.live_thread.quit()
            self.live_thread.wait()

    def start_capture(self):
        exposure_time_unit = self.camera_ui.get_exposure_unit()
        exposure_time = self.camera_ui.get_exposure_time(exposure_time_unit)
        total_frames = self.camera_ui.get_total_frames()
        average_frames = self.camera_ui.get_average_frames()
        print(total_frames, average_frames)
        if exposure_time is None or total_frames is None or average_frames is None:
            return
        if (total_frames % average_frames) != 0:
            QMessageBox.critical(
                self,
                "Invalid Input",
                "Total frames must be a multiple of average frames."
            )
            return
        if is_camera_connected() is False:
            QMessageBox.critical(
                self,
                "Camera Not Connected",
                "Please connect the camera before starting live view."
            )
            return
        date = get_current_date()
        if not os.path.exists(f"./{date}"):
            os.mkdir(f"./{date}")
        self.capture_thread = threading.Thread(
            target=capture_image,
            args=(self.camera_ui.capture_label, exposure_time, total_frames, average_frames, f"./{date}"),
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
