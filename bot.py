import requests
import time
from datetime import datetime

# === НАСТРОЙКИ ===
TWELVE_API_KEY = "3b3d5c079bc84be7b619678949b6a9e1"
TG_TOKEN = "8860899573:AAH5H-0_yfEZ2aWvMjLESIqVXATOSG7jTuA"
TG_CHAT_ID = "1638163747"
SYMBOL = "GBP/USD"
INTERVAL = "1h"
CHECK_EVERY_SECONDS = 300  # проверка каждые 5 минут

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": TG_CHAT_ID, "text": message})

def get_candles():
    url = "https://api.twelvedata.com/time_series"
    params = {
        "symbol": SYMBOL,
        "interval": INTERVAL,
        "outputsize": 10,
        "apikey": TWELVE_API_KEY
    }
    r = requests.get(url, params=params)
    data = r.json()
    if "values" not in data:
        return None
    candles = data["values"]
    # Возвращаем в хронологическом порядке (старые → новые)
    return list(reversed(candles))

def check_fvg(candles):
    alerts = []
    # Проверяем последние завершённые свечи (не текущую)
    for i in range(2, len(candles) - 1):
        prev2 = candles[i - 2]
        curr  = candles[i]

        high_prev2 = float(prev2["high"])
        low_prev2  = float(prev2["low"])
        high_curr  = float(curr["high"])
        low_curr   = float(curr["low"])
        time_curr  = curr["datetime"]

        # Бычий FVG: low свечи N > high свечи N-2
        if low_curr > high_prev2:
            alerts.append(f"🟢 Бычий FVG | GBPUSD H1\nВремя: {time_curr}\nЗона: {high_prev2:.5f} — {low_curr:.5f}")

        # Медвежий FVG: high свечи N < low свечи N-2
        if high_curr < low_prev2:
            alerts.append(f"🔴 Медвежий FVG | GBPUSD H1\nВремя: {time_curr}\nЗона: {high_curr:.5f} — {low_prev2:.5f}")

    return alerts

def main():
    print("Бот запущен...")
    send_telegram("✅ FVG бот запущен. Слежу за GBPUSD H1")
    
    seen = set()  # чтобы не дублировать уведомления

    while True:
        try:
            candles = get_candles()
            if candles:
                alerts = check_fvg(candles)
                for alert in alerts:
                    if alert not in seen:
                        send_telegram(alert)
                        seen.add(alert)
                        print(f"Отправлено: {alert}")
        except Exception as e:
            print(f"Ошибка: {e}")

        time.sleep(CHECK_EVERY_SECONDS)

if __name__ == "__main__":
    main()
