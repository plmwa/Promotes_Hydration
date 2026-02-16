from gpiozero import Servo
from time import sleep

servo = Servo(12, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)
servo.value = 1
sleep(5)
