from PyQt5.QtWidgets import (
    QWidget, QTabWidget, QVBoxLayout, QHBoxLayout, QPushButton, QMessageBox, QCheckBox, QComboBox,
    QLabel, QLineEdit, QApplication, QSizePolicy, QSpacerItem
)
from PyQt5.QtCore import Qt
import sys

class WelcomeScreen(QWidget):
    def __init__(self):
        super().__init__()

        self.setStyleSheet("""
            QWidget {
                background-color: #001f3f;
                color: white;
            }
            QLabel {
                font-size: 28px;
            }
            QLineEdit {
                padding: 8px;
                font-size: 16px;
                border-radius: 6px;
                border: 1px solid #ccc;
                background-color: #003366;
                color: white;
            }
            QLineEdit:placeholder {
                color: #bbbbbb;
            }

            QPushButton {
                color: white;
                background-color: #001f3f;
                border: 2px solid white;
                border-radius: 8px;
                padding: 8px 12px;
            }
            QPushButton:hover {
                background-color: #003366;
            }
            QPushButton:pressed {
                background-color: #004080;
            }
        """)

        

        # Main layout centered
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(100, 100, 100, 100)
        layout.setAlignment(Qt.AlignCenter)

        self.title = QLabel("Welcome to the IMPS4 Camera Control!")
        self.title.setAlignment(Qt.AlignCenter)

        self.name_input = QLineEdit()
        self.name_input.setFocusPolicy(Qt.ClickFocus)
        self.name_input.setPlaceholderText("Enter your name")
        self.name_input.setMaximumWidth(300)
        self.name_input.setAlignment(Qt.AlignCenter)

        self.continue_button = QPushButton("Continue")

        layout.addStretch()
        layout.addWidget(self.title, alignment=Qt.AlignCenter)
        layout.addWidget(self.name_input, alignment=Qt.AlignCenter)
        layout.addWidget(self.continue_button, alignment=Qt.AlignCenter)
        layout.addStretch()
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            QApplication.quit() 
            sys.exit(0)


class CameraTabsWidget(QWidget):
    def __init__(self, username):
        super().__init__()
        self.setWindowTitle("Camera Tabs")
        self.resize(1000, 800)

        self.setStyleSheet("background-color: #2e2e2e;")

        # Username label floating (not in layout)
        self.username_label = QLabel(username, self)
        self.username_label.setStyleSheet("""
            color: white;
            background-color: #001f3f;
            font-size: 20px;
        """)
        self.username_label.adjustSize()

        # Main layout for tabs
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.tabs = QTabWidget()
        self.tabs.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        main_layout.addWidget(self.tabs)

        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid white;
                background: #001f3f;
            }
            QTabBar::tab {
                background: white;
                color: #001f3f;
                border: 1px solid black;
                padding: 7px;
            }
            QTabBar::tab:selected {
                background: #555555;
            }
        """)


        # --------- Live View Tab ----------
        live_view_tab = QWidget()
        live_view_tab.setStyleSheet("background-color: #001f3f; color: white;")
        live_view_layout = QVBoxLayout(live_view_tab)

        self.live_view_label = QLabel("Live View Feed")
        self.live_view_label.setMinimumSize(600, 400)
        self.live_view_label.setFrameShape(QLabel.Box)
        self.live_view_label.setAlignment(Qt.AlignCenter)
        self.live_view_label.setStyleSheet("background-color: black; color: white;")

        live_view_layout.addStretch()
        live_view_layout.addWidget(self.live_view_label, alignment=Qt.AlignCenter)
        live_view_layout.addStretch()

        # --- Exposure info and input for Live View ---
        # --- Exposure section for Live View (left-aligned, like Capture) ---

        # Exposure info label above input
        live_exposure_info = QLabel("Max: 5 s | Min: 21 µs")
        live_exposure_info.setStyleSheet("color: white;")
        live_view_layout.addWidget(live_exposure_info, alignment=Qt.AlignLeft)

        # Exposure input row
        live_exposure_layout = QHBoxLayout()
        live_exposure_label = QLabel("Exposure Time:")
        self.live_exposure_line_edit = QLineEdit()
        self.live_exposure_line_edit.setPlaceholderText("Exposure time")
        self.live_exposure_line_edit.setMaximumWidth(200)

        self.live_exposure_unit_dropdown = QComboBox()
        self.live_exposure_unit_dropdown.addItems(["s", "ms", "µs"])
        self.live_exposure_unit_dropdown.setMaximumWidth(60)
        self.live_exposure_unit_dropdown.setStyleSheet("""
            QComboBox {
                border: 1px solid white;
                padding: 4px;
                background-color: #003366;
                color: white;
            }
        """)

        live_exposure_layout.addWidget(live_exposure_label)
        live_exposure_layout.addWidget(self.live_exposure_line_edit)
        live_exposure_layout.addWidget(self.live_exposure_unit_dropdown)
        live_exposure_layout.addStretch()

        live_view_layout.addLayout(live_exposure_layout)



        # --- Buttons for Live View ---
        live_view_buttons_layout = QHBoxLayout()
        self.start_live_view_button = QPushButton("Start Live View")
        self.stop_live_view_button = QPushButton("Stop Live View")
        live_view_buttons_layout.addWidget(self.start_live_view_button)
        live_view_buttons_layout.addWidget(self.stop_live_view_button)
        live_view_layout.addLayout(live_view_buttons_layout)


        self.tabs.addTab(live_view_tab, "Live View")

        # --------- Capture Tab ----------
        capture_tab = QWidget()
        capture_tab.setStyleSheet("background-color: #001f3f; color: white;")
        capture_layout = QVBoxLayout(capture_tab)

        self.capture_label = QLabel("Capture Feed")
        self.capture_label.setMinimumSize(600, 400)
        self.capture_label.setFrameShape(QLabel.Box)
        self.capture_label.setScaledContents(True)
        self.capture_label.setAlignment(Qt.AlignCenter)
        self.capture_label.setStyleSheet("background-color: black; padding: 20px; border: 2px solid #333;")

        capture_layout.addStretch()
        capture_layout.setContentsMargins(40, 40, 40, 40)
        capture_layout.addWidget(self.capture_label, alignment=Qt.AlignCenter)
        capture_layout.addStretch()

        # --- Input controls layout ---
        inputs_layout = QVBoxLayout()

        # Exposure info for Capture
        capture_exposure_info = QLabel("Max: 5 s | Min: 21 µs")
        inputs_layout.addWidget(capture_exposure_info, alignment=Qt.AlignLeft)

        # Exposure time (inline with dropdown)
        exposure_layout = QHBoxLayout()
        exposure_label = QLabel("Exposure Time:")
        self.exposure_line_edit = QLineEdit()
        self.exposure_line_edit.setPlaceholderText("Exposure time")
        self.exposure_line_edit.setMaximumWidth(200)

        self.exposure_unit_dropdown = QComboBox()
        self.exposure_unit_dropdown.addItems(["s", "ms", "µs"])
        self.exposure_unit_dropdown.setMaximumWidth(60)
        self.exposure_unit_dropdown.setStyleSheet("""
            QComboBox {
                border: 1px solid white;
                padding: 4px;
                background-color: #001f3f;
                color: white;
            }
        """)

        exposure_layout.addWidget(exposure_label)
        exposure_layout.addWidget(self.exposure_line_edit)
        exposure_layout.addWidget(self.exposure_unit_dropdown)
        exposure_layout.addStretch()
        inputs_layout.addLayout(exposure_layout)

        # Total frame count
        frame_layout = QHBoxLayout()
        frame_label = QLabel("# of Frames:")
        self.frame_line_edit = QLineEdit()
        self.frame_line_edit.setPlaceholderText("# of Frames")
        self.frame_line_edit.setMaximumWidth(200)
        frame_layout.addWidget(frame_label)
        frame_layout.addWidget(self.frame_line_edit)
        frame_layout.addStretch()
        inputs_layout.addLayout(frame_layout)

        # Average fram count
        average_layout = QHBoxLayout()
        average_label = QLabel("# of Averaged Frames:")
        self.average_line_edit = QLineEdit()
        self.average_line_edit.setPlaceholderText("# of Averaged Frames")
        self.average_line_edit.setMaximumWidth(200)
        self.average_checkbox = QCheckBox()
        average_layout.addWidget(average_label)
        average_layout.addWidget(self.average_line_edit)
        average_layout.addStretch()
        inputs_layout.addLayout(average_layout)

        # Add all input layouts to capture layout
        capture_layout.addLayout(inputs_layout)

        # Capture button centered
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.start_capture_button = QPushButton("Start Capture")
        button_layout.addWidget(self.start_capture_button)
        button_layout.addStretch()
        capture_layout.addLayout(button_layout)

        self.tabs.addTab(capture_tab, "Capture")



        # --------- Apply button styles ----------
        button_style = """
            QPushButton {
                color: white;
                background-color: #001f3f;
                border: 2px solid white;
                border-radius: 6px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #003366;
            }
            QPushButton:pressed {
                background-color: #004080;
            }
        """

        buttons = [self.start_live_view_button, self.stop_live_view_button, self.start_capture_button]
        for btn in buttons:
            btn.setMinimumSize(120, 65)
            btn.setStyleSheet(button_style)
            font = btn.font()
            font.setPointSize(11)
            btn.setFont(font)
        
        self.start_capture_button.setMinimumSize(350, 65)
        font = self.start_capture_button.font()
        font.setPointSize(13)
        self.start_capture_button.setFont(font)

    def get_exposure_time(self, exposure_time_unit):
        try:
            if exposure_time_unit == 's':
                exp_time = float(self.exposure_line_edit.text())
            elif exposure_time_unit == 'ms':
                exp_time = float(self.exposure_line_edit.text()) * 1e-3
            elif exposure_time_unit == 'µs':
                exp_time = float(self.exposure_line_edit.text()) * 1e-6

            if exp_time < 0:
                QMessageBox.critical(
                self,
                "Invalid Input",
                "Please enter a non-negative integer exposure time."
                )
                return None
            if exp_time > 5 or exp_time < (21 *1e-6):
                QMessageBox.critical(
                    self,
                    "Invalid Input",
                    "Live view exposure time must be between 21 µs and 5 s."
                )
                return None
        
            return exp_time
        except ValueError:
            QMessageBox.critical(
                self,
                "Invalid Input",
                "Please enter a valid integer for live view exposure  cagsdf time."
            )
            return None
    
    def get_live_exposure_time(self, exposure_time_unit):
        try:
            if exposure_time_unit == 's':
                exp_time = float(self.live_exposure_line_edit.text())
            elif exposure_time_unit == 'ms':
                exp_time = float(self.live_exposure_line_edit.text()) * 1e-3
            elif exposure_time_unit == 'µs':
                exp_time = float(self.live_exposure_line_edit.text()) * 1e-6

            if exp_time < 0:
                QMessageBox.critical(
                self,
                "Invalid Input",
                "Please enter a valid integer for live view exposure time."
                )
                return None
            if exp_time > 5 or exp_time < (21 *1e-6):
                QMessageBox.critical(
                    self,
                    "Invalid Input",
                    "Live view exposure time must be between 21 µs and 5 s."
                )
                return None
        except ValueError:
            QMessageBox.critical(
                self,
                "Invalid Input",
                "Please enter a valid integer for live view exposure time."
            )
            return None
        
    def get_total_frames(self):
        try:
            return int(self.frame_line_edit.text())
        except ValueError:
            QMessageBox.critical(
                self,
                "Invalid Input",
                "Please enter a valid integer for number of totalframes."
            )
            return None

    def get_average_frames(self):
        try:
            return int(self.average_line_edit.text())
        except ValueError:
            QMessageBox.critical(
                self,
                "Invalid Input",
                "Please enter a valid integer for number of totalframes."
            )
            return None
    def get_exposure_unit(self):
        return self.exposure_unit_dropdown.currentText()
    
    def get_live_exposure_unit(self):
        return self.live_exposure_unit_dropdown.currentText()
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            QApplication.quit()  # closes everything and stops the event loop
            sys.exit(0)