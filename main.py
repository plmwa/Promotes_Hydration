import time
import sys
import RPi.GPIO as GPIO
import csv 
from datetime import datetime 

# 作成したモジュールと設定をインポート
import config
from controllers.servo_controller import ServoController
from controllers.weight_sensor import WeightSensor

WEIGHT_LOG_FILE = "./waiting_log/weight_log.csv"

class HydrationMonitor:
    """
    水分補給を監視し、必要に応じて警告を出すメインアプリケーションクラス
    """
    def __init__(self):
        """
        各コンポーネントを初期化
        """
        self.sensor = WeightSensor(
            data_pin=config.HX711_DATA_PIN,
            clk_pin=config.HX711_CLK_PIN,
            reference_unit=config.HX711_REFERENCE_UNIT
        )
        self.servo = ServoController(
            pin=config.SERVO_PIN,
            min_angle=config.SERVO_MIN_ANGLE,
            max_angle=config.SERVO_MAX_ANGLE
        )
        self.last_significant_weight = 0
        self.initialize_log_file() # <--- 変更点: ログファイルの初期化メソッドを呼び出し

    # <--- 変更点: ログファイルを初期化するメソッドを追加 ---
    def initialize_log_file(self):
        """
        ログファイルが存在しない場合にヘッダーを書き込みます。
        """
        try:
            with open(WEIGHT_LOG_FILE, 'x', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'weight_g'])
                print(f"ログファイル '{WEIGHT_LOG_FILE}' を作成しました。")
        except FileExistsError:
            # ファイルが既に存在する場合は何もしない
            print(f"ログファイル '{WEIGHT_LOG_FILE}' を使用します。")
            pass

    # <--- 変更点: 重量データを記録するメソッドを追加 ---
    def log_weight(self, weight):
        """
        現在の日時と重量をCSVファイルに追記します。
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
            with open(WEIGHT_LOG_FILE, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([timestamp, f"{weight:.2f}"])
            print(f"\n[記録] {timestamp}, 重量: {weight:.2f} g")
        except IOError as e:
            print(f"\n[エラー] ログファイルへの書き込みに失敗しました: {e}")

    def wait_for_cup(self):
        """
        コップが置かれる（一定以上の重量が検知される）まで待機します。
        """
        print("\n--- 準備フェーズ ---")
        print(f"コップと水を置いてください。(約{config.WEIGHT_THRESHOLD_G}g以上のものを検知します)")
        
        while True:
            weight = self.sensor.get_weight(config.SENSOR_READ_TIMES)
            print(f"\r現在の重量: {weight:.2f} g", end="")
            if weight >= config.WEIGHT_THRESHOLD_G:
                self.last_significant_weight = weight
                print(f"\nコップを検知しました。初期重量: {self.last_significant_weight:.2f} g")
                time.sleep(2)
                self.last_significant_weight = self.sensor.get_weight(config.SENSOR_READ_TIMES)
                print(f"安定後の初期重量: {self.last_significant_weight:.2f} g")
                
                self.log_weight(self.last_significant_weight) # <--- 変更点: 重量データを記録
                break
            time.sleep(1)

    def monitor_drinking(self):
        """
        25分間、水分補給（重量変化）を監視します。
        """
        print("\n--- 監視フェーズ ---")
        print(f"{config.MONITORING_DURATION_S / 60:.0f}分間の監視を開始します。")
        
        start_time = time.time()
        while time.time() - start_time < config.MONITORING_DURATION_S:
            current_weight = self.sensor.get_weight(config.SENSOR_READ_TIMES)
            elapsed_time = time.time() - start_time
            
            print(f"\r現在の重量: {current_weight:.2f} g | 経過時間: {elapsed_time:.0f}秒", end="")

            weight_diff = self.last_significant_weight - current_weight
            
            if weight_diff >= config.WEIGHT_THRESHOLD_G:
                print(f"\n水分補給を検知しました！ 重量変化: {weight_diff:.2f} g")
                self.servo.move_to_max_angle()
                print("サーボを初期位置に戻しました。")
                self.wait_for_cup()  # コップが置かれるまで待機
                print("リセットします。")
                start_time = time.time()

            time.sleep(1)
        
        print(f"\n{config.MONITORING_DURATION_S / 60:.0f}分間、規定の重量変化がありませんでした。")
        return False



    def trigger_alert(self):
        """
        警告としてサーボモーターを回転させます。
        回転中に水分補給があれば中断します。
        """
        print("\n--- 警告フェーズ ---")
        # 警告開始時の重量を一旦取得
        alert_start_weight = self.sensor.get_weight(config.SENSOR_READ_TIMES)

        for angle in self.servo.rotate_slowly(config.ALERT_DURATION_S):
            print(f"\rサーボ回転中... 角度: {angle}度", end="")
            
            current_weight = self.sensor.get_weight(1)
            weight_diff = alert_start_weight - current_weight

            if weight_diff >= config.WEIGHT_THRESHOLD_G:
                print("\n警告中に水分補給を検知しました！")
                # サーボを-90度の初期位置に戻します
                self.servo.move_to_min_angle()
                print("サーボを初期位置に戻しました。")
                return
        print("\n警告動作が完了しました。これ以上水はこぼせません")
        self.servo.move_to_min_angle()

    def run(self):
        """
        プログラムのメインループ
        """
        self.servo.move_to_min_angle()
        self.wait_for_cup()

        while True:
            self.monitor_drinking()
            self.trigger_alert()
            self.wait_for_cup()


if __name__ == '__main__':
    try:
        monitor = HydrationMonitor()
        monitor.run()
    except (KeyboardInterrupt, SystemExit):
        print("\nプログラムを終了します。")
    finally:
        GPIO.cleanup()
        print("GPIOクリーンアップ完了。")