import cv2
import pytesseract
from PIL import Image

import stations
from modules.throttle_control import stop_train, update_speed

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

markerFile = open("./patterns/stop_markers.txt", "r")
lines = markerFile.readlines()

global marker_count
global close_to_station


def stop_detection(image):
    gray_img = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    # 25
    thresh = cv2.threshold(gray_img, 14, 255, cv2.THRESH_BINARY_INV)[1]

    text_detection_img = cv2.threshold(gray_img, 150, 255, cv2.THRESH_BINARY_INV)[1]

    contours = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[0]

    found_stop = False

    for contour in contours:
        (x, y, w, h) = cv2.boundingRect(contour)
        scale = round((w / h - 1) * 100)
        if w < 40 or h < 40 or w > 150 or h > 150 or scale < -50 or scale > 50 or y > 600 or y < 140:
            continue

        cropped = text_detection_img[y:+y + h, x:x + w]

        stop_marker_str = pytesseract.image_to_string(cropped,
                                                      config=r'--user-words patterns/stop_markers.txt --oem 3 --psm 8')

        if len(stop_marker_str) > 3 or len(stop_marker_str) == 0:
            continue
        found = False
        for line in lines:
            line = line.replace("\n", "")

            if line in stop_marker_str:
                found = True
                found_stop = True
                continue

        if found:
            cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 3)
            continue
        else:
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 3)

    global marker_count
    try:
        if marker_count is None:
            marker_count = 0
    except NameError:
        marker_count = 0

    if found_stop:
        if marker_count > 0:
            stop_train()
        else:
            marker_count += 1
    else:
        marker_count = 0

    print(marker_count)
    cv2.imshow("frame", image)
    cv2.moveWindow("frame", 1921, 0)


def approach_detection(screen, ui_data):
    if not ui_data['notis_str'] == '':
        return

    distance = ui_data['distance']
    global close_to_station
    try:
        if close_to_station is None:
            close_to_station = False
    except NameError:
        close_to_station = False
    if distance < 0.1:
        if distance > 0:
            update_speed(ui_data, 60)
            close_to_station = False
        else:
            if not close_to_station:
                close_to_station = True
                update_speed(ui_data, 15)

        if hasattr(stations, ui_data['station_name']):
            station_info = getattr(stations, ui_data['station_name'])
            if station_info[0] & (1 << 0):
                stop_detection(screen)
    elif distance < 0.2:
        update_speed(ui_data, 60)
    else:
        update_speed(ui_data, 200)
