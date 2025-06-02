from camera_gui import Ui_MainWindow
from camera_funcs import *
from PyQt5.QtWidgets import QApplication, QMainWindow
import sys
import threading

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.setup_connections()

    def setup_connections(self):
        self.ui.start_live_button.clicked.connect(self.start_live_button)

    def start_live_view(self):
        threading.Thread(target=live_view, args=(self.ui.live_label,), daemon=True).start()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())
