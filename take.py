import subprocess
import requests
import time
import datetime
import WEBHOOKS

WEBHOOK = WEBHOOKS.WEBHOOK

# Get device name from adb
def get_device_name():
    try:
        result = subprocess.run(
            ["adb", "shell", "getprop", "ro.product.model"],
            capture_output=True, text=True, check=True
        )
        name = result.stdout.strip()
        return name if name else "ADB Device"
    except Exception:
        return "ADB Device"

DEVICE_NAME = get_device_name()

def log_discord(message, level="INFO"):
    """Send log message to Discord webhook"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    content = f"[{timestamp}] [{level}] {message}"
    payload = {
        "username": DEVICE_NAME,
        "content": f"```{content}```"
    }
    try:
        requests.post(WEBHOOK, json=payload)
    except requests.exceptions.RequestException as e:
        pass  # Silently ignore logging failures


def auto_send(interval=10, DEVICE_NAME=None):
    if DEVICE_NAME is None:
        DEVICE_NAME = get_device_name()
    log_discord(f"Starting automatic screenshot sending every {interval} seconds...", "INFO")
    while True:
        try:
            # Capture screenshot from ADB
            process = subprocess.Popen(
                ["adb", "exec-out", "screencap", "-p"],
                stdout=subprocess.PIPE
            )
            image = process.stdout.read()
            
            if not image:
                log_discord("No screenshot captured from device.", "WARN")
                time.sleep(interval)  # Wait longer before trying again
                continue

            # Send screenshot to webhook as file
            data = {
                "username": DEVICE_NAME,
                "content": f"```{DEVICE_NAME} at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.```"
            }
            files = {"file": (f"{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.png", image, "image/png")}
            response = requests.post(WEBHOOK, files=files, data=data)

        except requests.exceptions.RequestException as req_err:
            log_discord(f"Network error: {req_err}", "ERROR")
        except Exception as e:
            log_discord(f"Unexpected error: {e}", "ERROR")

        time.sleep(interval)

if __name__ == "__main__":
    DEVICE_NAME = get_device_name()
    auto_send(interval=3, DEVICE_NAME=DEVICE_NAME)

