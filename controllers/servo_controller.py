from gpiozero import AngularServo
import time

class ServoController:
    """
    サーボモーターを制御するクラス
    """
    def __init__(self, pin, min_angle, max_angle):
        """
        サーボモーターを初期化します。
        """
        self.min_angle = min_angle
        self.max_angle = max_angle
        self.servo = AngularServo(
            pin,
            min_angle=min_angle,
            max_angle=max_angle,
            min_pulse_width=0.5 / 1000,
            max_pulse_width=2.4 / 1000
        )
        print("サーボモーターの準備ができました。")

    def move_to_min_angle(self):
        """
        サーボを最小角度（初期位置）に移動させます。
        """
        print(f"サーボを初期位置 ({self.min_angle}度) に移動します。")
        self.servo.angle = self.min_angle
        time.sleep(1) # 動作完了まで待機
        self.detach()

    def move_to_max_angle(self):
        """
        サーボを最大角度に移動させます。
        """
        print(f"サーボを最大位置 ({self.max_angle}度) に移動します。")
        self.servo.angle = self.max_angle/4
        time.sleep(0.5)
        self.servo.angle = self.max_angle/2
        time.sleep(0.5)
        self.servo.angle = self.max_angle
        time.sleep(1) # 動作完了まで待機
        self.detach()

    def move_to_max_angle_start(self):
        """
        サーボを最大角度に移動させます。
        """
        print(f"サーボを最大位置 ({self.max_angle}度) に移動します。")
        self.servo.angle = self.max_angle
        time.sleep(1) # 動作完了まで待機
        self.detach()

    def rotate_slowly(self, duration_sec):
        """
        指定された時間をかけて、最大角度から最小角度までゆっくり回転します。
        ジェネレータとして角度を1つずつ返します。
        """
        step_interval = duration_sec / ((self.max_angle - self.min_angle))
        print(f"{duration_sec}秒かけてサーボを回転させます...")
        print(step_interval)

        for angle in range(self.max_angle, self.min_angle, -1):
            self.servo.angle = angle
            yield angle  # 現在の角度を返す
            time.sleep(0.5)
            self.servo.angle = None
            time.sleep(step_interval)
            

    def detach(self):
        """
        サーボへの電力供給を停止し、ノイズや発熱を防ぎます。
        """
        self.servo.detach()