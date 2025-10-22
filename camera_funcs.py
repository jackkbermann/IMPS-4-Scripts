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
    error_text = pyqtSignal(str)  

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

                self.new_pixmap.emit(QPixmap(1, 1))

                while not self.stop_event.is_set():
                    gamma_value = getattr(self, 'gamma_value', 1.0)
                    camera.wait_for_new_image()
                    frame, _ = camera.image()
                    self.new_pixmap.emit(QPixmap.fromImage(u16_to_qimage(frame, autostretch=True, low_pct=0.5, high_pct=99.5, gamma=1.0)))

                
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

def u16_to_qimage(u16_image, invert=False, autostretch=True, low=None, high=None, low_pct=0.5, high_pct=99.5, gamma=1.0):
    a = u16_image
    if a.dtype != np.uint16:
        a = a.astype(np.uint16, copy=False)

    a = np.flipud(a)  

    if autostretch and (low is None or high is None):
        low, high = np.percentile(a, [low_pct, high_pct])
        if low >= high:  # guard
            low, high = 0, 65535

    if low is None:  low  = 0
    if high is None: high = 65535

    # gamma: <1 brightens midtones, >1 darkens
    # gamma first, then autostretch
    if gamma != 1.0:
        a = np.power(a.astype(np.float32) / 65535.0, 1.0 / gamma) * 65535.0


    scaled = (a - float(low)) / max(1.0, float(high - low))
    scaled = np.clip(scaled, 0.0, 1.0)


    # invert if needed
    if invert:
        scaled = 1.0 - scaled

    u8 = (scaled * 255.0 + 0.5).astype(np.uint8)
    h, w = u8.shape
    return QImage(u8.data, w, h, w, QImage.Format_Grayscale8).copy()



def capture_image(label, exposure_time, total_frames, average_frames, file_path, file_name, gamma_value, progress_queue=None):
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


    qimg = u16_to_qimage(images[-1], autostretch=True, low_pct=0.5, high_pct=99.5, gamma=gamma_value)
    label.setPixmap(QPixmap.fromImage(qimg))
    QApplication.processEvents()