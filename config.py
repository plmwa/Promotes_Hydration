# --- GPIOピン設定 ---
SERVO_PIN = 12       # サーボモーターの信号ピン
HX711_DATA_PIN = 5   # HX711のDATピン
HX711_CLK_PIN = 6    # HX711のSCKピン

# --- サーボモーター設定 ---
SERVO_MIN_ANGLE = -90
SERVO_MAX_ANGLE = 90

# --- センサー・ロジック設定 ---
# この値はご自身のセンサーに合わせて調整してください
# 121000/183 = 661 (1gあたりの値)
HX711_REFERENCE_UNIT = 661

# 重量変化として検出する最小値（グラム）
WEIGHT_THRESHOLD_G = 100

# 水分補給がないと判断する時間（秒）
# 25分 = 1500秒
MONITORING_DURATION_S = 30

#CUP_WEIGHT_G
CUP_WEIGHT_G = 205  # カップの重さ（グラム）

# 警告としてサーボを動かす時間（秒）
# 5分 = 300秒
ALERT_DURATION_S = 20

# 測定の安定性を高めるための読み取り回数
SENSOR_READ_TIMES = 5