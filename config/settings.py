"""
水分補給促進デバイスの設定クラス

すべての設定値を一元管理します。
環境変数や外部ファイルから設定を読み込むことも可能です。
"""
from dataclasses import dataclass
from typing import Final


@dataclass(frozen=True)
class GPIOPins:
    """GPIOピン設定"""
    SERVO: int = 12
    HX711_DATA: int = 5
    HX711_CLK: int = 6


@dataclass(frozen=True)
class ServoConfig:
    """サーボモーター設定"""
    MIN_ANGLE: int = -90
    MAX_ANGLE: int = 90
    MIN_PULSE_WIDTH: float = 0.5 / 1000  # 0.5ms
    MAX_PULSE_WIDTH: float = 2.4 / 1000  # 2.4ms


@dataclass(frozen=True)
class SensorConfig:
    """HX711センサー設定"""
    # この値は使用するセンサーに合わせて調整してください
    # 121000/183 = 661 (1gあたりの値)
    REFERENCE_UNIT: int = 717
    
    # 測定の安定性を高めるための読み取り回数
    READ_TIMES: int = 5


@dataclass(frozen=True)
class MonitoringConfig:
    """監視ロジック設定"""
    # 重量変化として検出する最小値（グラム）
    WEIGHT_THRESHOLD_G: int = 150
    
    # 水分補給がないと判断する時間（秒）
    # 本番: 25分 = 1500秒, テスト: 10秒
    MONITORING_DURATION_S: int = 10
    
    # コップの重さ（グラム）- 将来的な使用のため保持
    CUP_WEIGHT_G: int = 205
    
    # 警告としてサーボを動かす時間（秒）
    # 本番: 5分 = 300秒, テスト: 20秒
    ALERT_DURATION_S: int = 20


@dataclass(frozen=True)
class LoggingConfig:
    """ロギング設定"""
    LOG_DIR: str = "./waiting_log"
    LOG_FILENAME: str = "weight_log.csv"
    PROCESSED_LOG_DIR: str = "./processed_logs"


class Settings:
    """
    アプリケーション設定の中央管理クラス
    
    各設定グループへのアクセスを提供します。
    """
    def __init__(self):
        self.gpio = GPIOPins()
        self.servo = ServoConfig()
        self.sensor = SensorConfig()
        self.monitoring = MonitoringConfig()
        self.logging = LoggingConfig()
    
    @property
    def log_file_path(self) -> str:
        """ログファイルの完全パス"""
        return f"{self.logging.LOG_DIR}/{self.logging.LOG_FILENAME}"


# グローバル設定インスタンス（シングルトン）
settings = Settings()
