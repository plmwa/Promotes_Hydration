from hx711 import HX711
import RPi.GPIO as GPIO

class WeightSensor:
    """
    HX711重量センサーを制御するクラス
    """
    def __init__(self, data_pin, clk_pin, reference_unit):
        """
        センサーを初期化します。
        """
        try:
            self.hx = HX711(data_pin, clk_pin)
            self.hx.set_reading_format("MSB", "MSB")
            self.hx.set_reference_unit(reference_unit)
            self.reset_and_tare()
            print("重量センサーの準備ができました。")
        except Exception as e:
            print(f"HX711の初期化中にエラーが発生しました: {e}")
            GPIO.cleanup()
            exit()

    def reset_and_tare(self):
        """
        センサーをリセットし、風袋引き（ゼロ点調整）を行います。
        """
        self.hx.reset()
        self.hx.tare()
        print("センサーをリセットし、風袋引きを行いました。")

    def get_weight(self, times=5):
        """
        指定された回数重量を測定し、その平均値を返します。
        """
        try:
            # 負の値が返ってきた場合、0として扱う
            weight = max(0, self.hx.get_weight(times))
            return weight
        except Exception as e:
            print(f"重量の取得中にエラーが発生しました: {e}")
            return 0