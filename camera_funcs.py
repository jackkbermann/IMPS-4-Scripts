from PyQt5.QtWidgets import QApplication, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt
from pco import Camera
from constants import EXPOSURE_TIMES
import numpy as np 
import cv2
import glob
import os
import time
from camera_gui import *
from PIL import Image


def cv_to_qt(image):
    # Normalize 16-bit to 8-bit for display
    image_8bit = cv2.convertScaleAbs(image, alpha=(255.0/65535.0))
    h, w = image_8bit.shape
    qt_image = QImage(image_8bit.data, w, h, w, QImage.Format_Grayscale8)
    return QPixmap.fromImage(qt_image)

def live_view(label):
    with Camera() as camera:
        camera.record(number_of_images=10, mode='ring buffer')
        

        while True:
            camera.wait_for_new_image()
            image, meta = camera.image()

            pixmap = cv_to_qt(image)
            label.setPixmap(pixmap)  # update QLabel in GUI
            QApplication.processEvents()  # refresh GUI

            if cv2.waitKey(1) & 0xFF == ord('q'):
                camera.stop()
                break


# Single exposure image capture function
def capture_image(exposure_time, num_images, average, file_path):
    images = []
    # checks if file path exists, if not, create it
    if not os.path.exists(file_path):
        os.mkdir(file_path)
        
    with Camera() as camera:
        # set the exposure time
        camera.exposure_time = exposure_time
        camera.record(
            number_of_images=num_images,
            mode='ring buffer'
        )
    # wait for the camera to finish recording images
        while camera.recorded_image_count != num_images:
            time.sleep(0.001)

        camera.stop()

    # if average booolen is true, average the images
        if (average):
            image = camera.image_average()
            images.append(image)
            custom_name = f"my_custom_name.tif"
            Image.fromarray(image).save(os.path.join(file_path, custom_name))
        else:
            for i in range(num_images):
                image, meta = camera. image(image_index=i)
                images.append(image)
                custom_name = f"my_custom_name_{i+1:03d}.tif"
                Image.fromarray(image).save(os.path.join(file_path, custom_name))

    # Display the captured image
    cv2.imshow("Captured Image", images[-1]) # use cv2 module to display the image
    cv2.waitKey(0)
    cv2.destroyAllWindows()




       




    