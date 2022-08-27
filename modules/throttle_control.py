import time

import keyboard


def update_speed(ui_data, target_speed, max_speed=100):
    current_throttle = ui_data['throttle_percentage']
    speedlimit = ui_data['speedlimit']
    if target_speed > speedlimit:
        target_speed = speedlimit
    if target_speed > max_speed:
        target_speed = max_speed
    target = int(target_speed/max_speed*100)
    difference_throttle = target - current_throttle
    if -1 < difference_throttle < 1:
        return
    elif difference_throttle > 0:
        if difference_throttle < 5:
            keyboard.press_and_release("w")
        else:
            keyboard.press("w")
            time.sleep(difference_throttle * 0.025)
            keyboard.release("w")
    else:
        if difference_throttle > -5:
            keyboard.press_and_release("s")
        else:
            keyboard.press("s")
            time.sleep(abs(difference_throttle * 0.025))
            keyboard.release("s")


def stop_train():
    print("stopping")
    keyboard.press("s")
    time.sleep(5)
    keyboard.release("s")
