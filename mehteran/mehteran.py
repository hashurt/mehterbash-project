import os
import time
import requests
import subprocess

ORCHESTRATOR_URL = os.getenv("ORCHESTRATOR_URL", "http://localhost:5000")
AGENT_ID = os.getenv("AGENT_ID", "agent1")
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", 10))  # saniye

def register_agent():
    """Orchestrator'a kendini kaydeder"""
    try:
        res = requests.post(f"{ORCHESTRATOR_URL}/agents", json={"id": AGENT_ID})
        if res.status_code == 200:
            print(f"[mehteran] Agent '{AGENT_ID}' kaydedildi.")
        elif res.status_code == 400 and "zaten var" in res.text:
            print(f"[mehteran] Agent '{AGENT_ID}' zaten kayıtlı.")
        else:
            print(f"[mehteran] Agent kaydedilemedi: {res.text}")
    except Exception as e:
        print(f"[mehteran] Kayıt hatası: {e}")

def fetch_tasks():
    """Orchestrator'dan görev listesini çeker"""
    try:
        res = requests.get(f"{ORCHESTRATOR_URL}/tasks/{AGENT_ID}/list")
        if res.status_code == 200:
            return res.json()
        else:
            print(f"[mehteran] Görev çekme hatası: {res.status_code}")
            return []
    except Exception as e:
        print(f"[mehteran] Görev çekme hatası: {e}")
        return []

def execute_task(task):
    """Görevi çalıştırır"""
    print(f"[mehteran] Görev çalıştırılıyor: {task['command']}")
    try:
        output = subprocess.check_output(task["command"], shell=True, stderr=subprocess.STDOUT)
        print(f"[mehteran] Çıktı:\n{output.decode()}")
    except subprocess.CalledProcessError as e:
        print(f"[mehteran] Hata çıktısı:\n{e.output.decode()}")

def main():
    print(f"[mehteran] Agent '{AGENT_ID}' başlatıldı.")
    register_agent()

    last_run_times = {}

    while True:
        tasks = fetch_tasks()
        now = time.time()

        for task in tasks:
            if not task["enabled"]:
                continue

            task_id = task["id"]
            interval = task["interval"] or POLL_INTERVAL
            last_run = last_run_times.get(task_id, 0)

            if now - last_run >= interval:
                execute_task(task)
                last_run_times[task_id] = now

        time.sleep(1)

if __name__ == "__main__":
    main()
