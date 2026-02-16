"""
水分補給促進デバイス - メインプログラム

コップの重量を監視し、一定時間水分補給がない場合に
サーボモータでコップを傾けて警告を発します。
"""
import time
import RPi.GPIO as GPIO

from config.settings import settings
from controllers.servo_controller import ServoController
from controllers.weight_sensor import WeightSensor
from core.logger import WeightLogger
from core.state_machine import HydrationState, HydrationStateMachine


class HydrationMonitor:
    """
    水分補給を監視し、必要に応じて警告を出すメインアプリケーションクラス
    
    ステートマシンパターンを使用して状態遷移を管理し、
    重量センサーとサーボモーターを制御します。
    """
    
    def __init__(self):
        """各コンポーネントを初期化します"""
        print("=== 水分補給促進デバイスを初期化中 ===\n")
        
        # 設定の読み込み
        self.settings = settings
        
        # ロガーの初期化
        self.logger = WeightLogger(self.settings.log_file_path)
        
        # センサーの初期化
        self.sensor = WeightSensor(
            data_pin=self.settings.gpio.HX711_DATA,
            clk_pin=self.settings.gpio.HX711_CLK,
            reference_unit=self.settings.sensor.REFERENCE_UNIT
        )
        
        # サーボコントローラの初期化
        self.servo = ServoController(
            pin=self.settings.gpio.SERVO,
            min_angle=self.settings.servo.MIN_ANGLE,
            max_angle=self.settings.servo.MAX_ANGLE,
            min_pulse_width=self.settings.servo.MIN_PULSE_WIDTH,
            max_pulse_width=self.settings.servo.MAX_PULSE_WIDTH
        )
        
        # ステートマシンの初期化
        self.state_machine = HydrationStateMachine(
            monitoring_duration_s=self.settings.monitoring.MONITORING_DURATION_S
        )
        
        print("\n初期化完了！\n")

    def wait_for_cup(self) -> float:
        """
        コップが置かれる（一定以上の重量が検知される）まで待機します。
        
        Returns:
            float: 検知された安定後の重量（グラム）
        """
        self.state_machine.transition_to_idle()
        threshold = self.settings.monitoring.WEIGHT_THRESHOLD_G
        read_times = self.settings.sensor.READ_TIMES
        
        print(f"コップと水を置いてください。(約{threshold}g以上のものを検知します)")
        
        while True:
            weight = self.sensor.get_weight(read_times)
            print(f"\r現在の重量: {weight:.2f} g", end="")
            
            if weight >= threshold:
                print(f"\nコップを検知しました。初期重量: {weight:.2f} g")
                time.sleep(2)
                
                # 安定後の重量を再測定
                stable_weight = self.sensor.get_weight(read_times)
                print(f"安定後の初期重量: {stable_weight:.2f} g")
                
                # ログに記録
                self.logger.log_weight(stable_weight)
                
                return stable_weight
            
            time.sleep(1)
    
    def monitor_drinking(self) -> bool:
        """
        設定された時間、水分補給（重量変化）を監視します。
        
        Returns:
            bool: タイムアウトした場合False、水分補給があった場合はループ継続
        """
        threshold = self.settings.monitoring.WEIGHT_THRESHOLD_G
        read_times = self.settings.sensor.READ_TIMES
        
        print(f"[デバッグ] monitor_drinking開始 - 状態: {self.state_machine.state.name}")
        
        while not self.state_machine.is_monitoring_timeout():
            current_weight = self.sensor.get_weight(read_times)
            elapsed_time = self.state_machine.get_elapsed_monitoring_time()
            remaining_time = self.state_machine.get_remaining_monitoring_time()
            
            print(
                f"\r現在の重量: {current_weight:.2f} g | "
                f"経過: {elapsed_time:.0f}秒 | "
                f"残り: {remaining_time:.0f}秒",
                end=""
            )
            
            # 重量変化を確認
            weight_diff = self.state_machine.last_significant_weight - current_weight
            
            if weight_diff >= threshold:
                print(f"\n水分補給を検知しました！ 重量変化: {weight_diff:.2f} g")
                
                # サーボを初期位置に戻す
                self.servo.move_to_initial_position(gradual=True)
                
                # コップが置かれるまで待機
                new_weight = self.wait_for_cup()
                
                # タイマーをリセット（状態もMONITORINGに戻る）
                self.state_machine.reset_monitoring_timer(new_weight)
                print(f"[デバッグ] タイマーリセット後 - 状態: {self.state_machine.state.name}")
            
            time.sleep(1)
        
        duration_min = self.settings.monitoring.MONITORING_DURATION_S / 60
        print(f"\n{duration_min:.0f}分間、規定の重量変化がありませんでした。")
        print(f"[デバッグ] タイムアウト検知 - 警告動作に移行します")
        return False
    
    def trigger_alert(self) -> None:
        """
        警告としてサーボモーターを回転させます。
        回転中に水分補給があれば中断します。
        """
        self.state_machine.transition_to_alerting()
        
        threshold = self.settings.monitoring.WEIGHT_THRESHOLD_G
        alert_duration = self.settings.monitoring.ALERT_DURATION_S
        
        # 警告開始時の重量を取得
        alert_start_weight = self.sensor.get_weight(
            self.settings.sensor.READ_TIMES
        )
        
        # ゆっくり回転
        for angle in self.servo.rotate_slowly(alert_duration):
            print(f"\rサーボ回転中... 角度: {angle}度", end="")
            
            # 重量変化を確認（高速チェックのため1回のみ測定）
            current_weight = self.sensor.get_weight(1)
            weight_diff = alert_start_weight - current_weight
            
            if weight_diff >= threshold:
                print("\n警告中に水分補給を検知しました！")
                self.servo.move_to_initial_position(gradual=False)
                return
        
        print("\n警告動作が完了しました。")
        self.servo.move_to_initial_position(gradual=False)
    
    def run(self) -> None:
        """
        プログラムのメインループを実行します。
        
        1. サーボを初期位置に移動
        2. コップの設置を待機
        3. 水分補給を監視
        4. タイムアウト時に警告を発動
        5. 2に戻る
        """
        print("=== プログラムを開始します ===\n")
        
        # サーボを初期位置に移動
        self.servo.move_to_initial_position(gradual=False)
        
        # 最初のコップ設置を待機
        initial_weight = self.wait_for_cup()
        
        # 監視状態に遷移
        self.state_machine.transition_to_monitoring(initial_weight)
        
        # メインループ
        while True:
            # 水分補給を監視
            print("[デバッグ] 監視フェーズ開始")
            self.monitor_drinking()
            
            # 警告を発動
            print("[デバッグ] 警告フェーズ開始")
            self.trigger_alert()
            
            # 次のコップ設置を待機
            new_weight = self.wait_for_cup()
            
            # 監視を再開
            self.state_machine.transition_to_monitoring(new_weight)
    
    def cleanup(self) -> None:
        """リソースをクリーンアップします"""
        print("\nクリーンアップ中...")
        self.servo.cleanup()
        self.sensor.cleanup()
        GPIO.cleanup()
        print("クリーンアップ完了。")


def main():
    """メインエントリポイント"""
    monitor = None
    try:
        monitor = HydrationMonitor()
        monitor.run()
    except (KeyboardInterrupt, SystemExit):
        print("\n\nプログラムを終了します。")
    except Exception as e:
        print(f"\n\n予期しないエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if monitor:
            monitor.cleanup()


if __name__ == '__main__':
    main()
