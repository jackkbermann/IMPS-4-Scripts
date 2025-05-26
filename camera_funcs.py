import matplotlib.pyplot as plt
from pco import Camera
from constants import EXPOSURE_TIMES
import numpy as np 
import cv2

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



    