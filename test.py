from gpiozero import Servo
from time import sleep

# GPIO 12�ԃs���ɐڑ����ꂽ�T�[�{���[�^�[��������
# min_pulse_width��max_pulse_width�́A���g���̃T�[�{���[�^�[�̎d�l�ɍ��킹�Ē������Ă��������B
servo = Servo(12, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)

try:
    # 90�x����-60�x�܂ŁA-15�x���p�x��ύX
    # range(start, stop, step)���g�p
    for angle in range(90, -65, -15):
        # �p�x��-1����1�͈̔͂ɕϊ�
        # gpiozero��Servo���C�u�����ł́A�p�x��-90�x����90�x�͈̔͂ň����܂��B
        # ���̂��߁Avalue�v���p�e�B�ɂ�-1�i-90�x�j����1�i90�x�j�̒l��ݒ肵�܂��B
        servo.value = angle / 90.0
        # ���̓���܂�10�b�ԑҋ@
        sleep(1)
        servo.value = None
        sleep(5)

except KeyboardInterrupt:
    print("�v���O�������I�����܂���")

finally:
    # �v���O�����I�����ɃT�[�{���[�^�[�̓�����~
    servo.value = None