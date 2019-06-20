from gpiozero import LED, Button
from time import sleep

green_led = LED(17)
#amber_led = LED(27)
red_led = LED(22)
button = Button(26)

def await_knock():
    button.wait_for_press()

def open_door():
    green_led.on()
    sleep(2)
    green_led.off()

def reject_knock():
    red_led.on()
    sleep(2)
    red_led.off()
