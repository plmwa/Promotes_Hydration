import csv
from datetime import datetime
from supabase import create_client, Client
import os
from dotenv import load_dotenv
import uuid

# --- 設定項目 ---
LOG_FILE_PATH = "./waiting_log/weight_log.csv"
PROCESSED_LOGS_DIR = "processed_logs"

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
# 一旦仮置き
USER_ID = os.getenv("USER_ID")
GRAM_TO_ML = 1.0

def calculate_intake_from_csv(file_path):
    if not os.path.exists(file_path):
        print(f"エラー: ログファイル '{file_path}' が見つかりません。")
        return []

    events = []
    with open(file_path, 'r', newline='') as f:
        reader = csv.reader(f)
        try:
            header = next(reader)
            if 'timestamp' not in header[0]:
                f.seek(0)
        except StopIteration:
            return []

        for row in reader:
            try:
                events.append({
                    'timestamp': datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S'),
                    'weight': float(row[1])
                })
            except (ValueError, IndexError) as e:
                print(f"'{file_path}'の行'{row}'をスキップしました: {e}")
    
    events.sort(key=lambda x: x['timestamp'])

    intake_events = []
    for i in range(1, len(events)):
        prev_event = events[i-1]
        current_event = events[i]
        weight_diff = prev_event['weight'] - current_event['weight']

        if weight_diff > 0:
            intake_ml = int(weight_diff * GRAM_TO_ML)
            intake_events.append({
                'time': current_event['timestamp'],
                'amount': intake_ml
            })
            
    return intake_events

def sync_with_supabase(supabase: Client, user_id, intake_events: list):
    """
    計算された水分摂取量データをSupabaseに保存する（シンプル版）。
    重複データはデータベース側で自動的に無視されます。
    """
    if not intake_events:
        print("処理する新しいデータがありません。")
        return

    events_to_insert = [
        {
            'user_id': user_id,
            'event_time': e['time'].isoformat(),
            'intake_milliliters': e['amount']
        }
        for e in intake_events
    ]

    print(f"{len(events_to_insert)}件のイベントをSupabaseに登録試行します...")
    try:
        supabase.table("intake_events").upsert(
            events_to_insert,
            on_conflict="user_id, event_time"  # 同じuser_idで同じevent_timeのデータは上書きしない
        ).execute()
        
        print("データの同期が完了しました。（重複データは無視されました）")
    except Exception as e:
        print(f"データの登録中にエラーが発生しました: {e}")
    
def main():
    print(f"--- {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")
    
    all_intake_events = calculate_intake_from_csv(LOG_FILE_PATH)
    if not all_intake_events:
        print("ログファイルからイベントが検出されませんでした。処理を終了します。")
        return

    if not all([SUPABASE_URL, SUPABASE_KEY]):
        print("エラー: .envファイルにSUPABASE_URLとSUPABASE_KEYを設定してください。")
        return
    
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        print(f"Supabaseへの接続に失敗しました: {e}")
        return

    sync_with_supabase(supabase, USER_ID, all_intake_events)
    
    os.makedirs(PROCESSED_LOGS_DIR, exist_ok=True)
    try:
        base_filename = os.path.basename(LOG_FILE_PATH)
        timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
        new_path = os.path.join(PROCESSED_LOGS_DIR, f"{timestamp_str}_{base_filename}")
        os.rename(LOG_FILE_PATH, new_path)
        print(f"'{LOG_FILE_PATH}'を'{new_path}'に移動しました。")
    except OSError as e:
        print(f"'{LOG_FILE_PATH}'の移動中にエラーが発生しました: {e}")

    print("処理が完了しました。")

if __name__ == "__main__":
    main()