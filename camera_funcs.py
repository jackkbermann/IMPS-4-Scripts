import matplotlib.pyplot as plt
from pco import Camera
from constants import EXPOSURE_TIMES
import numpy as np 
import cv2
import glob
import os
import time
from PIL import Image

# Live view function to display camera feed in real-time
def live_view(camera, exposure_time):
    with Camera() as camera:
        camera.record( # Start recording images
            number_of_images=0,
            exposure_time=exposure_time,
            mode='ring buffer'
        )

        while True:
            camera.wait_for_new_image()  # required for live view
            image, meta = camera.image() # capture image

            cv2.imshow("Captured Image", image) # use cv2 module to display the image
            if cv2.waitKey(1) & 0xFF == ord('q'): # press 'q' to exit
                camera.stop()
                break

    cv2.destroyAllWindows()

# Single exposure image capture function
def capture_image(camera, exposure_time, num_images, average, file_path):
    images = []
    # checks if file path exists, if not, create it
    if not os.path.exists(file_path):
        os.mkdir(file_path)
        
    with Camera() as camera:
        camera.record(
            number_of_images=num_images,
            exposure_time=exposure_time,
            mode='sequence',
            file_path=file_path
        )
    # wait for the camera to finish recording images
    while camera.recorded_image_count != num_images:
        time.sleep(0.001)

    camera.stop()

    # if average booolen is true, average the images
    if (average):
        image = camera.image_average()
        images.add(image)
    else:
        for i in range(num_images):
            image, meta = camera. image(image_index=i)
            images.append(image)
    # save the images to the file path
    for i in range(num_images):
        custom_name = f"my_custom_name_{i+1:03d}.tif"
        Image.fromarray(img).save(os.path.join(filepath, custom_name))

    cv2.imshow("Captured Image", images[-1]) # use cv2 module to display the image
    cv2.waitKey(0)
    cv2.destroyAllWindows()




       




    