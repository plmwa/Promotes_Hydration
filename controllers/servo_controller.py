"""サーボモーター制御モジュール

gpiozeroライブラリを使用してサーボモーターを制御します。
"""
from gpiozero import AngularServo
import time
from typing import Generator


class ServoController:
    """
    サーボモーターを制御するクラス
    
    水分補給促進のためのコップ傾け動作を管理します。
    """
    
    def __init__(
        self,
        pin: int,
        min_angle: int,
        max_angle: int,
        min_pulse_width: float = 0.5 / 1000,
        max_pulse_width: float = 2.4 / 1000
    ):
        """
        サーボモーターを初期化します。
        
        Args:
            pin: GPIO番号
            min_angle: 最小角度
            max_angle: 最大角度
            min_pulse_width: 最小パルス幅（秒）
            max_pulse_width: 最大パルス幅（秒）
        """
        self.min_angle = min_angle
        self.max_angle = max_angle
        self.servo = AngularServo(
            pin,
            min_angle=min_angle,
            max_angle=max_angle,
            min_pulse_width=min_pulse_width,
            max_pulse_width=max_pulse_width
        )
        print("サーボモーターの準備ができました。")
    
    def move_to_angle(self, angle: int, duration: float = 1.0) -> None:
        """
        サーボを指定された角度に移動させます。
        
        Args:
            angle: 目標角度
            duration: 移動後の待機時間（秒）
        """
        self.servo.angle = angle
        time.sleep(duration)
    
    def move_to_initial_position(self, gradual: bool = False) -> None:
        """
        サーボを初期位置（最大角度）に移動させます。
        
        Args:
            gradual: Trueの場合、段階的に移動します
        """
        print(f"サーボを初期位置 ({self.max_angle}度) に移動します。")
        
        if gradual:
            # 段階的に移動（負荷軽減）
            quarter = self.max_angle / 4
            half = self.max_angle / 2
            
            self.move_to_angle(int(quarter), duration=0.5)
            self.move_to_angle(int(half), duration=0.5)
            self.move_to_angle(self.max_angle, duration=1.0)
        else:
            self.move_to_angle(self.max_angle, duration=1.0)
        
        self.detach()
        print("サーボを初期位置に戻しました。")
    
    def rotate_slowly(self, duration_sec: int) -> Generator[int, None, None]:
        """
        指定された時間をかけて、最大角度から最小角度までゆっくり回転します。
        
        警告動作として使用され、各角度でジェネレータとして値を返します。
        これにより、呼び出し側は各ステップで重量変化を確認できます。
        
        Args:
            duration_sec: 回転にかける時間（秒）
        
        Yields:
            int: 現在の角度
        """
        total_steps = self.max_angle - self.min_angle
        servo_move_time = 0.1  # サーボ移動の待機時間（秒）
        
        # 実際の待機時間からサーボ移動時間を引く
        step_interval = (duration_sec / total_steps) - servo_move_time
        if step_interval < 0:
            step_interval = 0
        
        print(f"{duration_sec}秒かけてサーボを回転させます...")
        print(f"総ステップ数: {total_steps}, ステップ間隔: {step_interval:.3f}秒")
        
        for angle in range(self.max_angle, self.min_angle - 1, -1):
            self.servo.angle = angle
            yield angle
            time.sleep(servo_move_time)
            
            # サーボへの電力供給を一時的に停止（発熱・ノイズ防止）
            self.servo.detach()
            
            if step_interval > 0:
                time.sleep(step_interval)
    
    def detach(self) -> None:
        """
        サーボへの電力供給を停止します。
        
        発熱やノイズを防ぐために、動作完了後は電力供給を停止します。
        """
        self.servo.detach()
    
    def cleanup(self) -> None:
        """
        サーボのクリーンアップを行います。
        
        プログラム終了時に呼び出してください。
        """
        self.detach()