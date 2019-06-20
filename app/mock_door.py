import time
import random

def button_handler():
    notify_knock()

def await_knock():
    #button.wait_for_press()
    rnum = random.randint(10,40)
    time.sleep(rnum)

def open_door():
    time.sleep(2)
    print('open door')

def reject_knock():
    time.sleep(2)
    print('reject knock')
