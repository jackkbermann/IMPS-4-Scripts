from PyQt5.QtWidgets import QApplication, QLabel
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from pco import Camera
import numpy as np
import os
import time
from PIL import Image


class LiveViewWorker(QObject):
    new_pixmap = pyqtSignal(QPixmap)
    finished   = pyqtSignal()
    error_text = pyqtSignal(str)     # <-- add this

    def __init__(self, stop_event, exposure_time):
        super().__init__()
        self.stop_event = stop_event
        self.exposure_time = exposure_time

    def run(self):
        print("Camera recording started for live view.")
        try:
            with Camera() as camera:
                camera.exposure_time = self.exposure_time
                camera.record(number_of_images=100, mode='ring buffer')

                # 👇 send a tiny ping so the label updates immediately
                self.new_pixmap.emit(QPixmap(1, 1))

                while not self.stop_event.is_set():
                    camera.wait_for_new_image()
                    frame, _ = camera.image()
                    self.new_pixmap.emit(u16_to_qpixmap(frame))
                
                camera.stop()
        except Exception as e:
            self.error_text.emit(f"LiveViewWorker error: {e}")
        finally:
            self.finished.emit()



def is_camera_connected():
    try:
        with Camera() as cam:
            return True
    except Exception:
        return False

def u16_to_qpixmap(u16_image, invert=False):
    """
    Fixed linear map from 0..65535 -> 0..255 for display.
    Dark stays black, saturated stays white.
    """
    import numpy as np
    from PyQt5.QtGui import QImage, QPixmap

    if u16_image.dtype != np.uint16:
        u16_image = u16_image.astype(np.uint16, copy=False)

    u16_image = np.flipud(u16_image)  # Flip vertically for correct orientation
    scaled = (u16_image >> 8).astype(np.uint8)   # 65536 → 256 levels

    if invert:
        scaled = 255 - scaled

    h, w = scaled.shape
    qimg = QImage(scaled.data, w, h, w, QImage.Format_Grayscale8).copy()
    return QPixmap.fromImage(qimg)


def capture_image(label, exposure_time, total_frames, average_frames, file_path, file_name, progress_queue=None):
    images = []
    if not os.path.exists(file_path):
        os.mkdir(file_path)

    done = 0
    # frame count needs to be >= 4
    frame_count = total_frames // average_frames

    for i in range(average_frames):
        with Camera() as camera:
            camera.exposure_time = exposure_time
            camera.record(number_of_images=frame_count, mode='ring buffer')

            while camera.recorded_image_count < frame_count:
                time.sleep(0.005)
                if progress_queue:
                    try:
                        progress_queue.put_nowait(done + camera.recorded_image_count)
                    except Exception:
                        pass

            camera.stop()

            image = camera.image_average()
            images.append(image)
            # save each image with unique name and 0 padding
            custom_name = f"{file_name}_{i:03d}.tif"
            im = Image.fromarray(image.astype(np.uint16), mode="I;16")
            # save in file directory as tiff file
            im.save(os.path.join(file_path, custom_name), compression="tiff_lzw")

        done += frame_count
        if progress_queue:
            try:
                progress_queue.put_nowait(done)
            except Exception:
                pass

    pixmap = u16_to_qpixmap(images[-1])
    label.setPixmap(pixmap)
    QApplication.processEvents()