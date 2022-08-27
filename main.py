import time

import cv2
import keyboard

import config
import stations
from modules.station_automations import stop_detection, approach_detection
from modules.uireader import ui_reader
from screengrabber import grab_screen

if __name__ == '__main__':
    print("Starting up drive assist")
    time.sleep(1)

    if config.DEBUG:
        stationFile = open("./patterns/stations.txt", "r")
        stationList = stationFile.readlines()
        for station in stationList:
            if not hasattr(stations, station.strip().replace(" ", "_").replace("-", "_").lower()):
                print(station.strip().replace(" ", "_").replace("-", "_").lower() + " = (0, 0, 0)")

    while True:
        screen = grab_screen(1920, 1080)
        start_milliseconds = time.time()

        ui = ui_reader(screen)

        if ui['station_name'] == '':
            print("No fun info skipping")
            continue

        print(ui)
        if config.features_enabled & 1 << 2:
            if ui['aws_status'] == 'alert':
                keyboard.press_and_release('q')
        print(config.features_enabled & (1 << 6))
        if config.features_enabled & (1 << 6):
            print("yes")
            approach_detection(screen, ui)

        stopMilliseconds = time.time()
        frameTime = round(1000 / config.FPS)
        totalTime = stopMilliseconds - start_milliseconds
        waitTime = frameTime - totalTime

        if waitTime > 0:
            cv2.waitKey(round(waitTime))
