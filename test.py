from gpiozero import Servo
from time import sleep

# GPIO 12�ԃs���ɐڑ����ꂽ�T�[�{���[�^�[���`
servo = Servo(12, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)

print("�T�[�{���[�^�[��90�x����-90�x�֓������܂��B")
print("Ctrl+C�ł��ł��I���ł��܂��B")

try:
    # 90�x����-90�x�܂ŁA-5�x�����[�v
    for angle in range(90, -91, -5):
        # �p�x (-90?90) ���T�[�{�̒l (-1.0?1.0) �ɕϊ�
        value = angle / 90.0
        servo.value = value
        print(f"���݂̊p�x: {angle}�x")
        sleep(1) # �e�X�e�b�v��0.1�b�ҋ@

    print("\n���삪�������܂����B")

except KeyboardInterrupt:
    print("\n�v���O�������I�����܂��B")