import cv2
import numpy as np
from PIL import ImageGrab


def grab_screen(width, height):
    img = ImageGrab.grab(bbox=(0, 0, width, height))
    # noinspection PyTypeChecker
    img_np = np.array(img)
    frame = cv2.cvtColor(img_np, cv2.COLOR_BGR2RGB)
    return frame


