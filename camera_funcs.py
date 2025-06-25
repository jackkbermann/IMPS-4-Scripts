from PyQt5.QtWidgets import QApplication, QLabel
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from pco import Camera
import numpy as np
import cv2
import os
import time
from PIL import Image


class LiveViewWorker(QObject):
    new_pixmap = pyqtSignal(QPixmap)
    finished = pyqtSignal()

    def __init__(self, stop_event, exposure_time, exposure_time_unit):
        super().__init__()
        self.stop_event = stop_event
        self.exposure_time = exposure_time
        self.exposure_time_unit = exposure_time_unit

    def run(self, exposure_time_unit, exposure_time):
        with Camera() as camera:
            if (exposure_time_unit == 'ms'):
                    camera.exposure_time = exposure_time * 1e-3
            elif (exposure_time_unit == 'µs'):
                camera.exposure_time = exposure_time * 1e-6
            else: 
                camera.exposure_time = exposure_time
            camera.record(number_of_images=100, mode='ring buffer')

            while not self.stop_event.is_set():
                camera.wait_for_new_image()
                image, _ = camera.image()
                pixmap = cv_to_qt(image)
                self.new_pixmap.emit(pixmap)
                time.sleep(0.01)  # avoid overloading the event loop

            camera.stop()
            self.finished.emit()

def is_camera_connected():
    try:
        with Camera() as cam:
            return True
    except Exception:
        return False

def cv_to_qt(image):
    image_8bit = cv2.convertScaleAbs(image, alpha=(255.0/65535.0))
    h, w = image_8bit.shape
    qt_image = QImage(image_8bit.data, w, h, w, QImage.Format_Grayscale8)
    return QPixmap.fromImage(qt_image)


def capture_image(label, exposure_time, total_frames, average_frames, exposure_time_unit, file_path):
    images = []
    if not os.path.exists(file_path):
        os.mkdir(file_path)

    # frame count needs to be >= 4
    frame_count = total_frames // average_frames
    
    for i in range(average_frames):
        with Camera() as camera:
            if (exposure_time_unit == 'ms'):
                    camera.exposure_time = exposure_time * 1e-3
            elif (exposure_time_unit == 'µs'):
                camera.exposure_time = exposure_time * 1e-6
            else: 
                camera.exposure_time = exposure_time

            camera.record(number_of_images=frame_count, mode='ring buffer')

            while camera.recorded_image_count != total_frames:
                time.sleep(0.001)

            camera.stop()

        image = camera.image_average()
        images.append(image)
        custom_name = f"my_custom_name.tif"
        Image.fromarray(image).save(os.path.join(file_path, custom_name))

    pixmap = cv_to_qt(images[-1])
    label.setPixmap(pixmap)
    QApplication.processEvents()



