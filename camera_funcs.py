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

    def __init__(self, stop_event, exposure_time):
        super().__init__()
        self.stop_event = stop_event
        self.exposure_time = exposure_time

    def run(self, exposure_time):
        with Camera() as camera:
            camera.exposure_time = exposure_time
            camera.record(number_of_images=100, mode='ring buffer')

            while not self.stop_event.is_set():
                camera.wait_for_new_image()
                image, _ = camera.image()
                pixmap = u16_to_qpixmap(image)
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

def u16_to_qpixmap(u16_image, p_low=1.0, p_high=99.0, gamma=1.0):
    """
    Convert a 16-bit grayscale numpy array to an 8-bit QPixmap.
    Uses percentile stretch (p_low..p_high) for clear on-screen contrast.
    """
    import numpy as np
    import cv2
    from PyQt5.QtGui import QImage, QPixmap

    if u16_image.dtype != np.uint16:
        u16_image = u16_image.astype(np.uint16, copy=False)

    # Robust autoscale: map the chosen percentile window to 0..255
    lo, hi = np.percentile(u16_image, (p_low, p_high))
    if hi <= lo:
        lo, hi = int(u16_image.min()), int(u16_image.max())
        if hi <= lo:  # completely flat image
            scaled = np.zeros_like(u16_image, dtype=np.uint8)
        else:
            scaled = ((u16_image - lo) * (255.0 / (hi - lo))).clip(0, 255).astype(np.uint8)
    else:
        scaled = ((u16_image - lo) * (255.0 / (hi - lo))).clip(0, 255).astype(np.uint8)

    if gamma and gamma != 1.0:
        inv = 1.0 / max(gamma, 1e-6)
        # Apply simple gamma in 8-bit space
        scaled = ((scaled.astype(np.float32) / 255.0) ** inv * 255.0).astype(np.uint8)

    h, w = scaled.shape
    qimg = QImage(scaled.data, w, h, w, QImage.Format_Grayscale8).copy()  # .copy() so memory is owned
    return QPixmap.fromImage(qimg)

def capture_image(label, exposure_time, total_frames, average_frames, file_path):
    images = []
    if not os.path.exists(file_path):
        os.mkdir(file_path)

    # frame count needs to be >= 4
    frame_count = total_frames // average_frames

    for i in range(average_frames):
        with Camera() as camera:
            camera.exposure_time = exposure_time
            camera.record(number_of_images=frame_count, mode='ring buffer')

            while camera.recorded_image_count != frame_count:
                time.sleep(0.001)

            camera.stop()

            image = camera.image_average()
            images.append(image)
            custom_name = f"my_custom_name{i}.tif"
            Image.fromarray(image).save(os.path.join(file_path, custom_name))

    pixmap = u16_to_qpixmap(image)(images[-1])
    label.setPixmap(pixmap)
    QApplication.processEvents()