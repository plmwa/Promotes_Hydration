# テストファイル

このディレクトリには開発・テスト用のファイルが含まれています。

## ファイル一覧

- `test.py` - HX711センサーの動作確認用スクリプト
- `example.py` - サーボモーターの簡易テスト用スクリプト

## 使用方法

### HX711センサーのテスト

```bash
python tests/test.py
```

センサーの値を確認し、必要に応じて `config/settings.py` の `REFERENCE_UNIT` を調整してください。

### サーボモーターのテスト

```bash
python tests/example.py
```

サーボモーターが正しく動作するかを確認できます。
