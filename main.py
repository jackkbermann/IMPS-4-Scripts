from camera_gui import *
from camera_funcs import *
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget, QMessageBox, QProgressDialog
from PyQt5.QtGui import QFont
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QThread, QTimer
from queue import Queue, Empty
import sys
import threading
from datetime import date


def get_current_date():
    return date.today()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # initializes main window
        self.setStyleSheet("background-color: #001f3f;")
        self.setWindowTitle("IMPS4 Camera Control")
        self.resize(1000, 800)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.welcome_screen = WelcomeScreen()
        self.stack.addWidget(self.welcome_screen)

        self.stop_event = threading.Event()
        self.live_thread = None  
        self.capture_thread = None    

        self.setup_done = False

        # Connect the continue button to transition
        self.welcome_screen.continue_button.clicked.connect(self.go_to_camera_ui)
        self.stack.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)


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
            QMessageBox.critical(self, "Camera Not Connected",
                                "Please connect the camera before starting live view.")
            return

        self.live_thread = QThread(self)
        self.live_worker = LiveViewWorker(self.stop_event, exposure_time)
        self.live_worker.moveToThread(self.live_thread)

        # When thread starts, invoke worker.run (no args now)
        self.live_thread.started.connect(self.live_worker.run)

        # Update label safely on the GUI thread
        self.live_worker.new_pixmap.connect(self.update_live_view)

        # Cleanup
        self.live_worker.finished.connect(self.live_thread.quit)
        self.live_worker.finished.connect(self.live_worker.deleteLater)
        self.live_thread.finished.connect(self.live_thread.deleteLater)

        self.live_worker.error_text.connect(
            lambda msg: QMessageBox.critical(self, "Live View Error", msg)
        )
        self.live_thread.start()
        self.camera_ui.live_status_label.setText("Status: Live")
        self.camera_ui.live_status_label.setStyleSheet("color: #66ff66; margin-top: 8px;")

    def update_live_view(self, pixmap):
        # Use the inner rect so padding/border aren’t included
        target_size = self.camera_ui.live_view_label.contentsRect().size()
        if target_size.width() <= 0 or target_size.height() <= 0:
            return
        scaled = pixmap.scaled(target_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.camera_ui.live_view_label.setPixmap(scaled)

    def stop_live_view(self):
        self.stop_event.set()
        if self.live_thread and self.live_thread.isRunning():
            self.live_thread.quit()
            self.live_thread.wait()
        self.camera_ui.live_status_label.setText("Status: Stopped")
        self.camera_ui.live_status_label.setStyleSheet("color: #ff6666; margin-top: 8px;")

    def start_capture(self):
        exposure_time_unit = self.camera_ui.get_exposure_unit()
        exposure_time = self.camera_ui.get_exposure_time(exposure_time_unit)
        total_frames = self.camera_ui.get_total_frames()
        average_frames = self.camera_ui.get_average_frames(total_frames)
        file_name = self.camera_ui.get_filename()
        if exposure_time is None or total_frames is None or average_frames is None:
            return
        if is_camera_connected() is False:
            QMessageBox.critical(
                self,
                "Camera Not Connected",
                "Please connect the camera before starting capture."
            )
            return
        date = get_current_date()
        if not os.path.exists(f"../IMPS-4 Data/{date}"):
            os.mkdir(f"../IMPS-4 Data/{date}")

        # --- modal progress dialog (blocks interaction) ---
        dlg = QProgressDialog("Preparing capture…", None, 0, total_frames, self)
        dlg.setWindowTitle("Capturing")
        dlg.setCancelButton(None)
        dlg.setWindowModality(Qt.ApplicationModal)
        dlg.setAutoClose(False)
        dlg.setAutoReset(False)
        dlg.setMinimumDuration(0)
        dlg.setValue(0)
        dlg.show()

        # disable tabs hard (optional; dialog modality already blocks clicks)
        self.camera_ui.tabs.setEnabled(False)

        # progress queue + polling timer
        pq = Queue()
        timer = QTimer(self)
        timer.setInterval(50)  # ms
        def pump_progress():
            updated = False
            while True:
                try:
                    cur = pq.get_nowait()
                except Empty:
                    break
                else:
                    dlg.setValue(cur)
                    dlg.setLabelText(f"Capturing… {cur}/{total_frames} frames")
                    updated = True
            # optional: close if somehow reached end early
            if updated and dlg.value() >= total_frames:
                timer.stop()
        timer.timeout.connect(pump_progress)
        timer.start()
        




        self.capture_thread = threading.Thread(
            target=capture_image,
            args=(self.camera_ui.capture_label, exposure_time, total_frames, average_frames, f"../IMPS-4 Data/{date}/", file_name, pq),
            daemon=True)
        
        def capture_finished():
            timer.stop()
            dlg.setValue(total_frames)
            dlg.close()
            self.camera_ui.tabs.setEnabled(True)
            # QMessageBox.information(self, "Capture Complete", "Image capture is complete.")
        
        
        self.capture_thread.start()
        finish_watch = QTimer(self)
        finish_watch.setInterval(100)
        def check_done():
            if not self.capture_thread.is_alive():
                finish_watch.stop()
                capture_finished()
        finish_watch.timeout.connect(check_done)
        finish_watch.start()

def main():

    QtWidgets.QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QtWidgets.QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    
    # Custom dark blue dialog stylesheet for QMessageBox
    APP_DIALOG_QSS = """
    /* Box chrome */
    QMessageBox {
        background-color: #001f3f;       /* your dark blue */
        border: 1px solid #6aa6ff;       /* subtle accent */
        font-family: "Calibri";     
    }
    /* Main text + informative text */
    QMessageBox QLabel {
        color: #ffffff;
        font-size: 12pt;
        font-family: "Calibri"
    }
    /* Optional Details area (when present) */
    QMessageBox QTextEdit {
        background-color: #003366;
        color: #e8eaed;
        border: 1px solid #2A2F36;
    }
    /* Buttons */
    QMessageBox QPushButton {
        background-color: #003366;
        color: #ffffff;
        border: 1px solid #6aa6ff;
        border-radius: 6px;
        padding: 6px 12px;
        font-family: "Calibri"
    }
    QMessageBox QPushButton:hover   { background-color: #004080; }
    QMessageBox QPushButton:pressed { background-color: #00264d; }

    /* Keep the icon background clean */
    QMessageBox QLabel#qt_msgboxex_icon_label { background: transparent; }
    """

    # append to any existing app stylesheet (so your page styles stay intact)
    app.setStyleSheet(app.styleSheet() + APP_DIALOG_QSS)
    app.setFont(QFont("Calibri", 18))

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()