import subprocess
import requests
import time
import WEBHOOKS
WEBHOOK = WEBHOOKS.WEBHOOK

def auto_send(interval=5):
    while True:
        process = subprocess.Popen(
            ["adb", "exec-out", "screencap", "-p"],
            stdout=subprocess.PIPE
        )
        image = process.stdout.read()

        files = {
            "file": ("screen.png", image, "image/png")
        }

        requests.post(WEBHOOK, files=files)

        print("🚀 Sent screenshot")
        time.sleep(interval)

auto_send(5)



