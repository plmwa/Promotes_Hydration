from gpiozero import Servo
from time import sleep

# GPIO 12�ԃs���ɐڑ����ꂽ�T�[�{���[�^�[���`
servo = Servo(12, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)

a=90
for i in range(10):
    servo.value = (a-i*15)/90
    sleep(1)
    servo.value = None
    sleep(5)
