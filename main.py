from camera_gui import *
from camera_funcs import *
from PyQt5.QtWidgets import QApplication, QMainWindow
import sys
import threading

    # def setup_connections(self):
    #     self.ui.start_live_view_button.clicked.connect(self.start_live_button)

    # def start_live_view(self):
    #     threading.Thread(target=live_view, args=(self.ui.live_view_label,), daemon=True).start()

import sys
from PyQt5.QtWidgets import QApplication
from camera_gui import CameraTabsWidget

def main():
    app = QApplication(sys.argv)
    window = CameraTabsWidget()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()