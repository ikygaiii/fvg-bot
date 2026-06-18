import requests
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

TWELVE_API_KEY = "3b3d5c079bc84be7b619678949b6a9e1"
TG_TOKEN = "8860899573:AAH5H-0_yfEZ2aWvMjLESIqVXATOSG7jTuA"
TG_CHAT_ID = "7923797130"
SYMBOL = "GBP/USD"
INTERVAL = "1h"
CHECK_EVERY_SECONDS = 300

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": TG_CHAT_ID, "text": message})

def get_candles():
    url = "https://api.twelvedata.com/time_series"
    params = {"symbol": SYMBOL, "interval": INTERVAL, "outputsize": 10, "apikey": TWELVE_API_KEY}
    r = requests.get(url, params=params)
    data = r.json()
    if "values" not in data:
        return None
    return list(reversed(data["values"]))

def check_fvg(candles):
    alerts = []
    for i in range(2, len(candles) - 1):
        prev2 = candles[i - 2]
        curr = candles[i]
        high_prev2 = float(prev2["high"])
        low_prev2 = float(prev2["low"])
        high_curr = float(curr["high"])
        low_curr = float(curr["low"])
        time_curr = curr["datetime"]
        if low_curr > high_prev2:
            alerts.append(f"🟢 Бычий FVG | GBPUSD H1\nВремя: {time_curr}\nЗона: {high_prev2:.5f} — {low_curr:.5f}")
        if high_curr < low_prev2:
            alerts.append(f"🔴 Медвежий FVG | GBPUSD H1\nВремя: {time_curr}\nЗона: {high_curr:.5f} — {low_prev2:.5f}")
    return alerts

def bot_loop():
    print("Бот запущен...")
    send_telegram("✅ FVG бот запущен. Слежу за GBPUSD H1")
    seen = set()
    while True:
        try:
            candles = get_candles()
            if candles:
                for alert in check_fvg(candles):
                    if alert not in seen:
                        send_telegram(alert)
                        seen.add(alert)
                        print(f"Отправлено: {alert}")
        except Exception as e:
            print(f"Ошибка: {e}")
        time.sleep(CHECK_EVERY_SECONDS)

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"FVG Bot running")
    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    threading.Thread(target=bot_loop, daemon=True).start()
    HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
