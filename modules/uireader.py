import difflib
import re

import cv2
from pytesseract import pytesseract

pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

markerFile = open("./patterns/stations.txt", "r")
lines = markerFile.readlines()

noti_file = open("./patterns/notifications.txt", "r")
noti_lines = noti_file.readlines()

global last_stage


def ui_reader(image):
    image_cropped = image[1000:1080, 660:1300]
    gray_img = cv2.cvtColor(image_cropped, cv2.COLOR_RGB2GRAY)
    thresh = cv2.threshold(gray_img, 100, 255, cv2.THRESH_BINARY_INV)[1]

    # Read station name
    station_name_img = thresh[28:52, 0:240]

    t_station_name = str(pytesseract.image_to_string(station_name_img,
                                                 config=r'--user-words patterns/stations.txt --oem 3 --psm 7'))
    station_name = get_closed_station(t_station_name)

    # read distance from next station
    distance_img = thresh[55:75, 0:180]
    distance_str = str(pytesseract.image_to_string(distance_img,
                                                 config=r'--user-patterns patterns/miles.txt --oem 3 --psm 7')).replace("\n", "")
    distance_found = re.search(r'\d+\.\d+', distance_str)
    distance = 0.0
    if distance_found:
        if float(distance_found.group()):
            distance = float(distance_found.group())

    # Read current throttle
    throttle_img = gray_img[2:74, 258:260]

    count = 0
    total = 0
    for pixel in throttle_img:
        total += 1
        if pixel[0] > 120:
            count += 1
    throttle_percentage = 0
    if count > 0:
        throttle_percentage = int((count/total)*100)

    # Speed limit
    speedlimit_img = thresh[33:48, 292:315]
    speedlimit_str = str(pytesseract.image_to_string(speedlimit_img,
                                                 config=r'--user-words patterns/speedlimit.txt --oem 3 --psm 8')).replace("\n", "").strip()
    speedlimit_sub = re.sub("[^0-9]", "", speedlimit_str)
    if not speedlimit_sub.isdigit():
        if speedlimit_str.startswith("w") or speedlimit_str.startswith("y"):
            speedlimit_sub = 30
        elif speedlimit_str.startswith("B"):
            speedlimit_sub = 80
        else:
            print("Cannot find speedlimit, defaulting to 5 mph", speedlimit_str)
            speedlimit_sub = 5

    # Signal status
    signal_thresh = cv2.threshold(gray_img, 125, 255, cv2.THRESH_BINARY_INV)[1]
    double_yellow = signal_thresh[15][575] == 0
    green = signal_thresh[30][575] == 0
    single_yellow = signal_thresh[45][575] == 0
    red = signal_thresh[60][575] == 0

    global last_stage
    try:
        if last_stage is None:
            last_stage = 'danger'
    except NameError:
        last_stage = 'danger'

    signal_status = last_stage

    if red and green or green:
        signal_status = 'proceed'
    elif red:
        signal_status = 'danger'
    elif double_yellow and single_yellow:
        signal_status = 'pre_caution'
    elif single_yellow:
        signal_status = 'caution'

    if signal_status != last_stage:
        last_stage = signal_status

    # aws
    aws_status = 'alert'
    if (image_cropped[35][520] == 0).all():
        aws_status = 'none'

    # notifications
    notis_cropped = image[910:940, 665:1250]
    notis_gray = cv2.cvtColor(notis_cropped, cv2.COLOR_RGB2GRAY)
    notis_thresh = cv2.threshold(notis_gray, 160, 255, cv2.THRESH_BINARY_INV)[1]

    notis_str = str(pytesseract.image_to_string(notis_thresh,
                                                 config=r'--user-words patterns/notifications.txt --oem 3 --psm 7')).replace("\n", "").strip()
    notis_str = get_closed_notification(notis_str)
    # points

    cv2.imshow("frame", notis_thresh)
    # cv2.moveWindow("frame", 1921, 0)

    return {"station_name": station_name, "distance": distance, 'throttle_percentage': throttle_percentage, 'speedlimit': int(speedlimit_sub),
            'signal_status': signal_status, 'aws_status': aws_status, 'notis_str': notis_str}


def get_closed_station(text):
    current_best = ("", 0)
    for station in lines:
        ratio = difflib.SequenceMatcher(None, text, station).ratio()
        if ratio < 0.7:
            continue
        if ratio > current_best[1]:
            current_best = (station, ratio)
    return current_best[0].strip().replace(" ", "_").replace("-", "_").lower()


def get_closed_notification(text):
    current_best = ("", 0)
    for noti in noti_lines:
        ratio = difflib.SequenceMatcher(None, text, noti).ratio()
        if ratio < 0.7:
            continue
        if ratio > current_best[1]:
            current_best = (noti, ratio)
    return current_best[0].strip()
