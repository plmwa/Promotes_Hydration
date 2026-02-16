"""重量センサー制御モジュール

HX711を使用してロードセルからの重量データを読み取ります。
"""
import RPi.GPIO as GPIO
from typing import Optional
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from utils.hx711 import HX711


class WeightSensor:
    """
    HX711重量センサーを制御するクラス
    """
    
    def __init__(self, data_pin: int, clk_pin: int, reference_unit: int):
        """
        センサーを初期化します。
        
        Args:
            data_pin: HX711のDATピン番号
            clk_pin: HX711のSCKピン番号
            reference_unit: 参照単位（キャリブレーション値）
        
        Raises:
            RuntimeError: センサーの初期化に失敗した場合
        """
        try:
            self.hx = HX711(data_pin, clk_pin)
            self.hx.set_reading_format("MSB", "MSB")
            self.hx.set_reference_unit(reference_unit)
            self.reset_and_tare()
            print("重量センサーの準備ができました。")
        except Exception as e:
            error_msg = f"HX711の初期化中にエラーが発生しました: {e}"
            print(error_msg)
            GPIO.cleanup()
            raise RuntimeError(error_msg) from e
    
    def reset_and_tare(self) -> None:
        """
        センサーをリセットし、風袋引き（ゼロ点調整）を行います。
        """
        self.hx.reset()
        self.hx.tare()
        print("センサーをリセットし、風袋引きを行いました。")
    
    def get_weight(self, times: int = 5) -> float:
        """
        指定された回数重量を測定し、その平均値を返します。
        
        Args:
            times: 測定回数（平均化のため）
        
        Returns:
            float: 測定された重量（グラム）。エラー時は0.0
        """
        try:
            weight = self.hx.get_weight(times)
            return float(weight)
        except Exception as e:
            print(f"重量の取得中にエラーが発生しました: {e}")
            return 0.0
    
    def is_ready(self) -> bool:
        """
        センサーが測定準備できているかを確認します。
        
        Returns:
            bool: 準備できている場合True
        """
        try:
            return self.hx.is_ready()
        except Exception:
            return False
    
    def cleanup(self) -> None:
        """
        センサーのクリーンアップを行います。
        
        プログラム終了時に呼び出してください。
        """
        try:
            self.hx.power_down()
        except Exception as e:
            print(f"センサーのクリーンアップ中にエラーが発生しました: {e}")