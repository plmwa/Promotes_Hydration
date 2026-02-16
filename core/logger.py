"""
重量データのロギングを管理するモジュール

CSVファイルへの重量データ記録を担当します。
"""
import csv
import os
from datetime import datetime
from pathlib import Path
from typing import Optional


class WeightLogger:
    """
    重量データをCSVファイルに記録するクラス
    """
    
    def __init__(self, log_file_path: str):
        """
        ロガーを初期化します。
        
        Args:
            log_file_path: ログファイルのパス
        """
        self.log_file_path = log_file_path
        self._ensure_log_directory()
        self._initialize_log_file()
    
    def _ensure_log_directory(self) -> None:
        """ログディレクトリが存在することを確認します"""
        log_dir = Path(self.log_file_path).parent
        log_dir.mkdir(parents=True, exist_ok=True)
    
    def _initialize_log_file(self) -> None:
        """
        ログファイルが存在しない場合にヘッダーを書き込みます。
        """
        try:
            with open(self.log_file_path, 'x', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'weight_g'])
                print(f"ログファイル '{self.log_file_path}' を作成しました。")
        except FileExistsError:
            # ファイルが既に存在する場合は何もしない
            print(f"ログファイル '{self.log_file_path}' を使用します。")
    
    def log_weight(self, weight: float, timestamp: Optional[datetime] = None) -> bool:
        """
        指定された日時と重量をCSVファイルに追記します。
        
        Args:
            weight: 記録する重量（グラム）
            timestamp: 記録する日時（省略時は現在時刻）
        
        Returns:
            bool: 記録に成功した場合True
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        timestamp_str = timestamp.strftime('%Y-%m-%d %H:%M:%S')
        
        try:
            with open(self.log_file_path, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([timestamp_str, f"{weight:.2f}"])
            print(f"\n[記録] {timestamp_str}, 重量: {weight:.2f} g")
            return True
        except IOError as e:
            print(f"\n[エラー] ログファイルへの書き込みに失敗しました: {e}")
            return False
    
    def get_log_file_size(self) -> int:
        """
        ログファイルのサイズを取得します。
        
        Returns:
            int: ファイルサイズ（バイト）、ファイルが存在しない場合は0
        """
        try:
            return os.path.getsize(self.log_file_path)
        except OSError:
            return 0
