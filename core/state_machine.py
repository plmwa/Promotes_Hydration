"""
水分補給監視システムの状態管理モジュール

ステートマシンパターンを使用してシステムの状態遷移を管理します。
"""
from enum import Enum, auto
from typing import Optional
import time


class HydrationState(Enum):
    """
    システムの状態を表す列挙型
    """
    IDLE = auto()           # アイドル状態（コップ待ち）
    MONITORING = auto()     # 監視状態（水分補給を監視中）
    ALERTING = auto()       # 警告状態（サーボ動作中）


class HydrationStateMachine:
    """
    水分補給監視システムの状態を管理するクラス
    
    状態遷移のロジックを集約し、各状態での動作を管理します。
    """
    
    def __init__(self, monitoring_duration_s: int):
        """
        ステートマシンを初期化します。
        
        Args:
            monitoring_duration_s: 監視時間（秒）
        """
        self._state = HydrationState.IDLE
        self._monitoring_duration_s = monitoring_duration_s
        self._monitoring_start_time: Optional[float] = None
        self._last_significant_weight: float = 0.0
    
    @property
    def state(self) -> HydrationState:
        """現在の状態を取得します"""
        return self._state
    
    @property
    def last_significant_weight(self) -> float:
        """最後に記録された有意な重量を取得します"""
        return self._last_significant_weight
    
    def transition_to_monitoring(self, initial_weight: float) -> None:
        """
        監視状態に遷移します。
        
        Args:
            initial_weight: 初期重量（グラム）
        """
        self._state = HydrationState.MONITORING
        self._last_significant_weight = initial_weight
        self._monitoring_start_time = time.time()
        print(f"\n--- 監視フェーズ ---")
        print(f"{self._monitoring_duration_s / 60:.0f}分間の監視を開始します。")
        print(f"[デバッグ] 状態: MONITORING, 基準重量: {initial_weight:.2f}g")
    
    def transition_to_alerting(self) -> None:
        """警告状態に遷移します"""
        self._state = HydrationState.ALERTING
        self._monitoring_start_time = None
        print("\n--- 警告フェーズ ---")
    
    def transition_to_idle(self) -> None:
        """アイドル状態に遷移します"""
        self._state = HydrationState.IDLE
        self._monitoring_start_time = None
        print("\n--- 準備フェーズ ---")
    
    def reset_monitoring_timer(self, new_weight: float) -> None:
        """
        監視タイマーをリセットします。
        
        Args:
            new_weight: 新しい基準重量（グラム）
        """
        self._state = HydrationState.MONITORING
        self._monitoring_start_time = time.time()
        self._last_significant_weight = new_weight
        print("\nタイマーをリセットしました。監視を継続します。")
        print(f"[デバッグ] 状態: MONITORING (リセット), 基準重量: {new_weight:.2f}g, 監視時間: {self._monitoring_duration_s}秒")
    
    def get_elapsed_monitoring_time(self) -> float:
        """
        監視開始からの経過時間を取得します。
        
        Returns:
            float: 経過時間（秒）。監視中でない場合は0.0
        """
        if self._state != HydrationState.MONITORING or self._monitoring_start_time is None:
            return 0.0
        return time.time() - self._monitoring_start_time
    
    def is_monitoring_timeout(self) -> bool:
        """
        監視時間が経過したかどうかを判定します。
        
        Returns:
            bool: タイムアウトした場合True
        """
        if self._state != HydrationState.MONITORING:
            return False
        elapsed = self.get_elapsed_monitoring_time()
        is_timeout = elapsed >= self._monitoring_duration_s
        if is_timeout:
            print(f"\n[デバッグ] タイムアウト検知: {elapsed:.1f}秒 >= {self._monitoring_duration_s}秒")
        return is_timeout
    
    def get_remaining_monitoring_time(self) -> float:
        """
        監視の残り時間を取得します。
        
        Returns:
            float: 残り時間（秒）
        """
        if self._state != HydrationState.MONITORING:
            return 0.0
        elapsed = self.get_elapsed_monitoring_time()
        remaining = self._monitoring_duration_s - elapsed
        return max(0.0, remaining)
