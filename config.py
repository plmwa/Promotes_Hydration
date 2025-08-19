# --- GPIOピン設定 ---
SERVO_PIN = 12       # サーボモーターの信号ピン
HX711_DATA_PIN = 6   # HX711のDATピン
HX711_CLK_PIN = 5    # HX711のSCKピン

# --- サーボモーター設定 ---
SERVO_MIN_ANGLE = -90
SERVO_MAX_ANGLE = 90

# --- センサー・ロジック設定 ---
# この値はご自身のセンサーに合わせて調整してください
HX711_REFERENCE_UNIT = 114

# 重量変化として検出する最小値（グラム）
WEIGHT_THRESHOLD_G = 1000

# 水分補給がないと判断する時間（秒）
# 25分 = 1500秒
MONITORING_DURATION_S = 1500

# 警告としてサーボを動かす時間（秒）
# 5分 = 300秒
ALERT_DURATION_S = 300

# 測定の安定性を高めるための読み取り回数
SENSOR_READ_TIMES = 5