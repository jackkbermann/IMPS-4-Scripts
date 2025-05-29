import camera_funcs
from pco import Camera
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
import sys


# print("Welcome to the IMPS-4 Control Center!\n")
# print("--- CMOS Functions ---")
# print("1. Capture Image")
# print("3. Live View")
# print("4. Exit")

# camera_funcs.live_view()  # Example exposure time in ms



# min exposure time is 21us, max exposure time is 5000ms
camera_funcs.capture_image(10e-3, 5, True,"C:/Users/lab/Desktop/IMPS-4 Data/test")