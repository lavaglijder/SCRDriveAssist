import time

import cv2
import keyboard

import config
import routes
import stations
import trains
from modules.station_automations import stop_detection, approach_detection
from modules.uireader import ui_reader
from screengrabber import grab_screen

if __name__ == '__main__':
    print("Starting up drive assist")
    train = 'train_' + input("What train are you using? For example 458_0: ")
    while not hasattr(trains, train):
        print(train)
        train = 'train_' +  input("Unknown train name please try again: ")
    train_info = getattr(trains, train)

    route = 'route_' + input("What route are you driving? For example R001: ")
    while not hasattr(routes, route):
        route = 'route_' + input("Unknown route, please try again: ")
    route_info = getattr(routes, route)
    route_info[0] = str(route_info[0]).strip().replace(" ", "_").lower()
    route_info[1] = str(route_info[1]).strip().replace(" ", "_").lower()

    bound = input("Are you going north or south bound? Answer either north or south: ")
    while not bound == 'north' and not bound == 'south':
        bound = input("Invalid answer: ")

    if config.DEBUG:
        stationFile = open("./patterns/stations.txt", "r")
        stationList = stationFile.readlines()
        for station in stationList:
            station = station.strip()
            if station.startswith("#") or station == '':
                continue
            if not hasattr(stations, station.replace(" ", "_").replace("-", "_").lower()):
                print(station.replace(" ", "_").replace("-", "_").lower() + " = (0, 0, 0)")

    print("Waiting 3 seconds for you to get ready")
    time.sleep(3)

    while True:
        screen = grab_screen(1920, 1080)
        start_milliseconds = time.time()

        ui = ui_reader(screen)
        if bound == 'south':
            ui['destination'] = route_info[1]
        else:
            ui['destination'] = route_info[0]

        if ui['station_name'] == '':
            print("No fun info skipping")
            continue

        ui['train_features'] = train_info[0]
        ui['train_coaches'] = train_info[1]
        ui['max_train_speed'] = train_info[2]

        print(ui)
        if config.features_enabled & 1 << 2:
            if ui['aws_status'] == 'alert':
                keyboard.press_and_release('q')

        if config.features_enabled & (1 << 6):
            approach_detection(screen, ui)

        if config.features_enabled & (1 << 4) and ui['distance'] < 0.2:
            if ui['notis_str'] == 'Press T to close doors':
                keyboard.press_and_release('t')
            elif ui['notis_str'] == 'Press T to open doors':
                keyboard.press_and_release('t')
            elif ui['notis_str'] == 'Press T to begin loading':
                keyboard.press_and_release('t')

        stopMilliseconds = time.time()
        frameTime = round(1000 / config.FPS)
        totalTime = stopMilliseconds - start_milliseconds
        waitTime = frameTime - totalTime

        if waitTime > 0:
            cv2.waitKey(round(waitTime))
