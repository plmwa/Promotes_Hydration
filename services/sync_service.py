"""
Supabase同期サービスモジュール

ローカルのCSVログファイルからデータを読み取り、
Supabaseデータベースに同期します。
"""
import csv
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any
from supabase import create_client, Client
from dotenv import load_dotenv


class SupabaseSyncService:
    """
    SupabaseデータベースとCSVログファイルを同期するクラス
    """
    
    def __init__(
        self,
        log_file_path: str,
        processed_logs_dir: str,
        cup_weight_g: int = 205,
        gram_to_ml: float = 1.0
    ):
        """
        同期サービスを初期化します。
        
        Args:
            log_file_path: ログファイルのパス
            processed_logs_dir: 処理済みログファイルの保存先ディレクトリ
            cup_weight_g: コップの重量（グラム）
            gram_to_ml: グラムからミリリットルへの変換係数
        """
        load_dotenv()
        
        self.log_file_path = log_file_path
        self.processed_logs_dir = processed_logs_dir
        self.cup_weight_g = cup_weight_g
        self.gram_to_ml = gram_to_ml
        
        # 環境変数から設定を読み込み
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        self.user_id = os.getenv("USER_ID")
        
        self.supabase_client: Optional[Client] = None
    
    def _validate_config(self) -> bool:
        """
        設定が有効かどうかを確認します。
        
        Returns:
            bool: 設定が有効な場合True
        """
        if not all([self.supabase_url, self.supabase_key]):
            print("エラー: .envファイルにSUPABASE_URLとSUPABASE_KEYを設定してください。")
            return False
        
        if not self.user_id:
            print("警告: USER_IDが設定されていません。")
            return False
        
        return True
    
    def connect(self) -> bool:
        """
        Supabaseに接続します。
        
        Returns:
            bool: 接続に成功した場合True
        """
        if not self._validate_config():
            return False
        
        try:
            self.supabase_client = create_client(self.supabase_url, self.supabase_key)
            print("Supabaseへの接続に成功しました。")
            return True
        except Exception as e:
            print(f"Supabaseへの接続に失敗しました: {e}")
            return False
    
    def calculate_intake_events(self) -> List[Dict[str, Any]]:
        """
        CSVファイルから水分摂取イベントを計算します。
        
        Returns:
            List[Dict]: 摂取イベントのリスト
        """
        if not os.path.exists(self.log_file_path):
            print(f"エラー: ログファイル '{self.log_file_path}' が見つかりません。")
            return []
        
        events = []
        
        try:
            with open(self.log_file_path, 'r', newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                
                # ヘッダーをスキップ
                try:
                    header = next(reader)
                    if 'timestamp' not in header[0]:
                        f.seek(0)  # ヘッダーがない場合は最初から読む
                except StopIteration:
                    return []
                
                for row in reader:
                    try:
                        events.append({
                            'timestamp': datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S'),
                            'weight': float(row[1])
                        })
                    except (ValueError, IndexError) as e:
                        print(f"'{self.log_file_path}'の行'{row}'をスキップしました: {e}")
        except IOError as e:
            print(f"ログファイルの読み取り中にエラーが発生しました: {e}")
            return []
        
        # タイムスタンプ順にソート
        events.sort(key=lambda x: x['timestamp'])
        
        # 摂取イベントを計算
        intake_events = []
        for i in range(1, len(events)):
            prev_event = events[i - 1]
            current_event = events[i]
            weight_diff = prev_event['weight'] - current_event['weight']
            
            if weight_diff > 0:
                # 重量が減少した場合（水分補給があった）
                intake_ml = int(weight_diff * self.gram_to_ml)
                intake_events.append({
                    'time': current_event['timestamp'],
                    'amount': intake_ml
                })
            elif weight_diff < -10:
                # 重量が大幅に増加した場合（水の補充）
                intake_ml = int(prev_event['weight'] - self.cup_weight_g)
                if intake_ml > 0:
                    intake_events.append({
                        'time': current_event['timestamp'],
                        'amount': intake_ml
                    })
        
        return intake_events
    
    def sync_to_supabase(self, intake_events: List[Dict[str, Any]]) -> bool:
        """
        計算された摂取イベントをSupabaseに同期します。
        
        Args:
            intake_events: 摂取イベントのリスト
        
        Returns:
            bool: 同期に成功した場合True
        """
        if not intake_events:
            print("処理する新しいデータがありません。")
            return True
        
        if not self.supabase_client:
            print("エラー: Supabaseに接続されていません。")
            return False
        
        events_to_insert = [
            {
                'user_id': self.user_id,
                'event_time': e['time'].isoformat(),
                'intake_milliliters': e['amount']
            }
            for e in intake_events
        ]
        
        print(f"{len(events_to_insert)}件のイベントをSupabaseに登録試行します...")
        
        try:
            self.supabase_client.table("intake_events").upsert(
                events_to_insert,
                on_conflict="user_id, event_time"
            ).execute()
            
            print("データの同期が完了しました。（重複データは無視されました）")
            return True
        except Exception as e:
            print(f"データの登録中にエラーが発生しました: {e}")
            return False
    
    def archive_log_file(self) -> bool:
        """
        処理済みログファイルをアーカイブします。
        
        Returns:
            bool: アーカイブに成功した場合True
        """
        # 処理済みログディレクトリを作成
        Path(self.processed_logs_dir).mkdir(parents=True, exist_ok=True)
        
        try:
            base_filename = os.path.basename(self.log_file_path)
            timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
            new_path = os.path.join(
                self.processed_logs_dir,
                f"{timestamp_str}_{base_filename}"
            )
            
            os.rename(self.log_file_path, new_path)
            print(f"'{self.log_file_path}'を'{new_path}'に移動しました。")
            return True
        except OSError as e:
            print(f"'{self.log_file_path}'の移動中にエラーが発生しました: {e}")
            return False
    
    def run_sync(self) -> bool:
        """
        完全な同期プロセスを実行します。
        
        Returns:
            bool: 同期に成功した場合True
        """
        print(f"--- {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")
        
        # 摂取イベントを計算
        intake_events = self.calculate_intake_events()
        if not intake_events:
            print("ログファイルからイベントが検出されませんでした。処理を終了します。")
            return False
        
        # Supabaseに接続
        if not self.connect():
            return False
        
        # データを同期
        if not self.sync_to_supabase(intake_events):
            return False
        
        # ログファイルをアーカイブ
        if not self.archive_log_file():
            return False
        
        print("処理が完了しました。")
        return True


def calculate_intake_from_csv(
    file_path: str,
    cup_weight_g: int = 205,
    gram_to_ml: float = 1.0
) -> List[Dict[str, Any]]:
    """
    CSVファイルから水分摂取量を計算する簡易関数
    
    Args:
        file_path: CSVファイルのパス
        cup_weight_g: コップの重量（グラム）
        gram_to_ml: グラムからミリリットルへの変換係数
    
    Returns:
        List[Dict]: 摂取イベントのリスト
    """
    service = SupabaseSyncService(
        log_file_path=file_path,
        processed_logs_dir="./processed_logs",
        cup_weight_g=cup_weight_g,
        gram_to_ml=gram_to_ml
    )
    return service.calculate_intake_events()


def main():
    """メイン関数（スタンドアロン実行用）"""
    service = SupabaseSyncService(
        log_file_path="./waiting_log/weight_log.csv",
        processed_logs_dir="./processed_logs"
    )
    service.run_sync()


if __name__ == "__main__":
    main()
