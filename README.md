# 水分補給促進デバイス

コップの重量を監視し、一定時間水分補給がない場合にサーボモータでコップを傾けて警告を発する水分補給促進デバイスです。

## プロジェクト構成

```
Promotes_Hydration/
├── config/                  # 設定モジュール
│   ├── __init__.py
│   └── settings.py         # 全設定を一元管理
├── controllers/            # ハードウェア制御
│   ├── __init__.py
│   ├── servo_controller.py # サーボモーター制御
│   └── weight_sensor.py    # 重量センサー制御
├── core/                   # コアロジック
│   ├── __init__.py
│   ├── logger.py          # ロギング処理
│   └── state_machine.py   # ステートマシン
├── services/              # 外部サービス連携
│   ├── __init__.py
│   └── sync_service.py    # Supabase同期処理
├── utils/                 # ユーティリティ
│   ├── __init__.py
│   └── hx711.py          # HX711ドライバ
├── tests/                 # テストファイル
│   ├── __init__.py
│   ├── README.md
│   ├── test.py           # センサーテスト
│   └── example.py        # サーボテスト
├── waiting_log/           # 重量ログ（CSV）
├── processed_logs/        # 処理済みログ
├── main.py               # メインプログラム
├── requirements.txt      # 依存パッケージ
└── README.md            # このファイル
```

## 主な機能

1. **重量監視**: HX711センサーでコップの重量を常時監視
2. **タイマー管理**: コップ設置で監視開始、水分補給でタイマーリセット
3. **警告動作**: タイムアウト時にサーボモーターでコップを傾ける
4. **割り込み処理**: サーボ動作中も重量変化を検知し、即座に停止
5. **データロギング**: 重量データをCSVに記録
6. **クラウド同期**: Supabaseへデータを同期（オプション）

## セットアップ

### 1. 依存パッケージのインストール

```bash
python -m venv myvenv
source myvenv/bin/activate
pip install -r requirements.txt
```

### 2. 設定のカスタマイズ

`config/settings.py` で以下の設定を調整：

- **GPIOピン番号**: 使用するピンに合わせて変更
- **HX711 REFERENCE_UNIT**: センサーのキャリブレーション値
- **監視時間**: 本番/テスト環境に応じて調整
- **重量閾値**: 検出する重量変化の最小値

### 3. センサーのキャリブレーション

```bash
python tests/test.py
```

センサーの値を確認し、`config/settings.py`の`REFERENCE_UNIT`を調整してください。

## 実行方法

### メインプログラムの起動

```bash
python main.py
```

### Supabaseへのデータ同期

`.env`ファイルを作成し、以下の環境変数を設定：

```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
USER_ID=your_user_id
```

同期スクリプトを実行：

```bash
python -m services.sync_service
```

cron等で定期実行することも可能です。

## ハードウェア構成

- **Raspberry Pi**: メイン制御ユニット
- **HX711**: ロードセル用ADC
- **ロードセル**: 重量測定
- **サーボモーター**: コップ傾け機構

### 配線（デフォルト）

- サーボモーター信号線: GPIO 12
- HX711 DATA: GPIO 5
- HX711 CLK: GPIO 6

## 設計思想

### ステートマシンパターン

システムは3つの状態を持ちます：

- **IDLE**: アイドル状態（コップ待ち）
- **MONITORING**: 監視状態（水分補給を監視中）
- **ALERTING**: 警告状態（サーボ動作中）

### 非ブロッキング設計

- サーボ動作中もセンサー値を読み取り可能
- ジェネレータパターンで割り込み処理を実現

### モジュール分離

- 責務ごとにモジュールを分離
- 設定の一元管理
- テスタビリティの向上

## 開発

### コーディング規約

- Python 3.7+
- 型ヒントを使用
- docstringの記述
- 適切なエラーハンドリング

### デバッグ

設定ファイルで監視時間を短縮してテスト：

```python
# config/settings.py内のMonitoringConfigクラス
MONITORING_DURATION_S: int = 10  # 10秒（テスト用）
ALERT_DURATION_S: int = 20       # 20秒（テスト用）
```

## トラブルシューティング

### センサーが反応しない

1. 配線を確認
2. `tests/test.py`で値を確認
3. `config/settings.py`の`REFERENCE_UNIT`を調整

### サーボが動かない

1. GPIOピン番号を確認
2. `tests/example.py`で動作確認
3. パルス幅設定を調整

### 重量が不安定

1. センサーの固定を確認
2. 読み取り回数（`READ_TIMES`）を増やす
3. 環境ノイズを減らす

## リファクタリングの変更点

### 新しい構造の利点

1. **モジュール化**: 責務ごとにファイルを分離
2. **設定の一元化**: dataclassを使用した型安全な設定管理
3. **ステートマシン**: 明確な状態遷移管理
4. **ロギングの分離**: 専用クラスで管理
5. **型ヒント**: コードの可読性と保守性向上
6. **エラーハンドリング**: より堅牢なエラー処理

### 旧ファイルについて

- `config.py.old`: 旧設定ファイル（新しい`config/settings.py`を使用してください）
- `database/sync_supabase.py`: 旧同期スクリプト（新しい`services/sync_service.py`を使用してください）

## 参考文献

- [gpiozero Documentation](https://gpiozero.readthedocs.io/)
- [HX711 Python Library](https://github.com/tatobari/hx711py)