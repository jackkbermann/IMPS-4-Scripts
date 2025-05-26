import camera_funcs
from pco import Camera
from PyQt5.QtWidgets import QApplication, QMainWindow

camera = Camera()




print("Welcome to the IMPS-4 Control Center!\n")
print("--- CMOS Functions ---")
print("1. Capture Image")
print("3. Live View")
print("4. Exit")


camera_funcs.live_view(camera, exposure_time=1000)  # Example exposure time in ms