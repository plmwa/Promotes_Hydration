# Promotes_Hydration — Documentation

このドキュメントは `Promotes_Hydration` の使い方

## 概要
`Promotes_Hydration` は、重さセンサー（HX711 等）とサーボモーターを用いてユーザーの水分摂取を監視・記録し、Supabase に同期する仕組みを提供します。ローカルには `waiting_log` に未同期ログを蓄積し、`database/sync_supabase.py` で同期処理を行って `processed_logs` に保存します。

## クイックスタート
1. 仮想環境を有効化
```bash
source myenv/bin/activate
```

2. `config.py` を編集して Supabase 情報や GPIO ピンを指定

3. メインアプリケーションを実行

```bash
python main.py
```

4. ログを手動で同期

```bash
python3 database/sync_supabase.py
```

## ファイル／ディレクトリ説明
- `main.py` : プログラムのエントリ。センサー読み取り・ログ記録・サーボ制御を行う。
- `config.py` : 動作設定と外部サービス情報。
- `controllers/servo_controller.py` : サーボ制御ロジック。
- `controllers/weight_sensor.py` : 重量取得ロジック（HX711ラッパー等）。
- `database/sync_supabase.py` : `waiting_log` を Supabase に同期し、処理済みデータを `processed_logs` に保存する。
- `waiting_log/` : 同期前のログファイル格納場所。
- `processed_logs/` : 同期済みのログを格納するディレクトリ。
