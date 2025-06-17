from PyQt5.QtWidgets import QApplication, QLabel
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt
from pco import Camera
import numpy as np
import cv2
import os
import time
from PIL import Image

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

def live_view(label, stop_event, exposure_time):
    with Camera() as camera:
        camera.exposure_time = exposure_time * 10e-3
        print(camera.exposure_time)
        camera.record(number_of_images=100, mode='ring buffer')

        while not stop_event.is_set():
            camera.wait_for_new_image()
            image, meta = camera.image()
            pixmap = cv_to_qt(image)
            label.setPixmap(pixmap)
            QApplication.processEvents()

        camera.stop()

def capture_image(label, exposure_time, num_images, average, file_path):
    images = []
    if not os.path.exists(file_path):
        os.mkdir(file_path)

    with Camera() as camera:
        camera.exposure_time = exposure_time * 10e-3
        camera.record(number_of_images=num_images, mode='ring buffer')

        while camera.recorded_image_count != num_images:
            time.sleep(0.001)

        camera.stop()

        if average:
            image = camera.image_average()
            images.append(image)
            custom_name = f"my_custom_name.tif"
            Image.fromarray(image).save(os.path.join(file_path, custom_name))
        else:
            for i in range(num_images):
                image, meta = camera.image(image_index=i)
                images.append(image)
                custom_name = f"my_custom_name_{i+1:03d}.tif"
                Image.fromarray(image).save(os.path.join(file_path, custom_name))

    pixmap = cv_to_qt(images[-1])
    label.setPixmap(pixmap)
    QApplication.processEvents()



