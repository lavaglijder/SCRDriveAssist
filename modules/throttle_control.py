import time

import keyboard


def update_speed(ui_data, target_speed):
    max_speed = ui_data['max_train_speed']
    current_throttle = ui_data['throttle_percentage']
    speedlimit = ui_data['speedlimit']
    if target_speed > speedlimit:
        target_speed = speedlimit
    if target_speed > max_speed:
        target_speed = max_speed
    target = int(target_speed/max_speed*100)
    print(target)
    difference_throttle = target - current_throttle
    if -3 < difference_throttle < 0:
        return
    elif difference_throttle > 0:
        if difference_throttle < 5:
            keyboard.press("w")
            time.sleep(0.01)
            keyboard.release("w")
        else:
            keyboard.press("w")
            time.sleep(difference_throttle * 0.025)
            keyboard.release("w")
    else:
        if difference_throttle > -5:
            keyboard.press("s")
            time.sleep(0.01)
            keyboard.release("s")
        else:
            keyboard.press("s")
            time.sleep(abs(difference_throttle * 0.025))
            keyboard.release("s")


def stop_train():
    print("stopping")
    keyboard.press("s")
    time.sleep(5)
    keyboard.release("s")
