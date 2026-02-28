#!/usr/bin/env python3
import sys
import subprocess
import signal
from time import sleep
from gpiozero import LED, Button
from signal import pause

# 引数からデバイス名を取得
if len(sys.argv) < 2:
    sys.exit(1)
device = f"/dev/{sys.argv[1]}"

# GPIO 17番ピンにLED、22番ピンにボタンを設定
status_led = LED(17)
button = Button(22, hold_time=3)

# ---- 追加部分：強制終了(SIGTERM)を受け取った時の処理 ----
def cleanup_and_exit(signum, frame):
    status_led.off()  # LEDを確実に消す
    sys.exit(0)       # 安全にプログラムを終了

# systemdからSIGTERMが送られてきたら、上の関数を実行するように設定
signal.signal(signal.SIGTERM, cleanup_and_exit)
# ----------------------------------------------------------

# 1. 差し込んだら点灯（ボタン長押し待機状態）
status_led.on()

# 2. ボタンが3秒間長押しされるまでループして待機
while not button.is_held:
    sleep(0.1)

# 3. 処理中：点滅（0.2秒間隔）に変更してフォーマット開始を明示
status_led.blink(on_time=0.2, off_time=0.2)

try:
    # FAT32フォーマットの実行
    subprocess.run(['mkfs.fat', '-F', '32', device], check=True)
    subprocess.run(['sync'], check=True)
    
    # 4. 完了：消灯（抜いてOKのサイン）
    status_led.off()

except subprocess.CalledProcessError:
    # エラー発生時
    status_led.blink(on_time=0.1, off_time=0.9)

# 5. プログラムを維持
pause()
