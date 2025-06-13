from PyQt5.QtWidgets import (
    QWidget, QTabWidget, QVBoxLayout, QHBoxLayout, QPushButton, QMessageBox, QCheckBox,
    QLabel, QLineEdit
)
from PyQt5.QtCore import Qt

class CameraTabsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Camera Tabs")
        self.resize(1000, 800)

        # Whole window background
        self.setStyleSheet("background-color: #2e2e2e;")

        main_layout = QVBoxLayout(self)

        tabs = QTabWidget()
        main_layout.addWidget(tabs)

        # Style the tab bar
        tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #444444;
                background: #001f3f;
            }
            QTabBar::tab {
                background: #333333;
                color: white;
                padding: 10px;
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
        self.live_view_label.setMinimumSize(800, 600)
        self.live_view_label.setFrameShape(QLabel.Box)
        self.live_view_label.setAlignment(Qt.AlignCenter)
        self.live_view_label.setStyleSheet("background-color: black; color: white;")

        live_view_layout.addStretch()
        live_view_layout.addWidget(self.live_view_label, alignment=Qt.AlignCenter)
        live_view_layout.addStretch()

        # --- Exposure input for Live View ---
        live_exposure_layout = QHBoxLayout()
        live_exposure_label = QLabel("Exposure Time:")
        self.live_exposure_line_edit = QLineEdit()
        self.live_exposure_line_edit.setPlaceholderText("Exposure time (ms)")
        self.live_exposure_line_edit.setMaximumWidth(300)

        live_exposure_layout.addWidget(live_exposure_label)
        live_exposure_layout.addWidget(self.live_exposure_line_edit)
        live_exposure_layout.addStretch()
        live_view_layout.addLayout(live_exposure_layout)

        # --- Buttons for Live View ---
        live_view_buttons_layout = QHBoxLayout()
        self.start_live_view_button = QPushButton("Start Live View")
        self.stop_live_view_button = QPushButton("Stop Live View")
        live_view_buttons_layout.addWidget(self.start_live_view_button)
        live_view_buttons_layout.addWidget(self.stop_live_view_button)
        live_view_layout.addLayout(live_view_buttons_layout)


        tabs.addTab(live_view_tab, "Live View")

        # --------- Capture Tab ----------
        capture_tab = QWidget()
        capture_tab.setStyleSheet("background-color: #001f3f; color: white;")
        capture_layout = QVBoxLayout(capture_tab)

        self.capture_label = QLabel("Capture Feed")
        self.capture_label.setMinimumSize(800, 600)
        self.capture_label.setFrameShape(QLabel.Box)
        self.capture_label.setAlignment(Qt.AlignCenter)
        self.capture_label.setStyleSheet("background-color: black; color: white;")

        capture_layout.addStretch()
        capture_layout.addWidget(self.capture_label, alignment=Qt.AlignCenter)
        capture_layout.addStretch()

        # --- Input controls layout ---
        inputs_layout = QVBoxLayout()

        # Exposure time (inline)
        exposure_layout = QHBoxLayout()
        exposure_label = QLabel("Exposure Time:")
        self.exposure_line_edit = QLineEdit()
        self.exposure_line_edit.setPlaceholderText("Exposure time (ms)")
        self.exposure_line_edit.setMaximumWidth(200)
        exposure_layout.addWidget(exposure_label)
        exposure_layout.addWidget(self.exposure_line_edit)
        exposure_layout.addStretch()
        inputs_layout.addLayout(exposure_layout)

        # Frame count (inline)
        frame_layout = QHBoxLayout()
        frame_label = QLabel("# of Frames:")
        self.frame_line_edit = QLineEdit()
        self.frame_line_edit.setPlaceholderText("# of Frames")
        self.frame_line_edit.setMaximumWidth(200)
        frame_layout.addWidget(frame_label)
        frame_layout.addWidget(self.frame_line_edit)
        frame_layout.addStretch()
        inputs_layout.addLayout(frame_layout)

        # Average checkbox (label left, box right)
        average_layout = QHBoxLayout()
        average_label = QLabel("Average Images:")
        self.average_checkbox = QCheckBox()
        average_layout.addWidget(average_label)
        average_layout.addWidget(self.average_checkbox)
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

        tabs.addTab(capture_tab, "Capture")



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
                background-color: #000d1a;
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

    def get_exposure_time(self):
        try:
            return int(self.exposure_line_edit.text())
        except ValueError:
            QMessageBox.critical(
                self,
                "Invalid Input",
                "Please enter a valid integer for exposure time."
            )
            return None
    
    def get_live_exposure_time(self):
        try:
            return int(self.live_exposure_line_edit.text())
        except ValueError:
            QMessageBox.critical(
                self,
                "Invalid Input",
                "Please enter a valid integer for live view exposure time."
            )
            return None
    def get_num_frames(self):
        try:
            return int(self.frame_line_edit.text())
        except ValueError:
            QMessageBox.critical(
                self,
                "Invalid Input",
                "Please enter a valid integer for number of frames."
            )
            return None

    def get_average_bool(self):
        return self.average_checkbox.isChecked()
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()