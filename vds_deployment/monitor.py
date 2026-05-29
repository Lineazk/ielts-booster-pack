import sys
import subprocess
import time
import requests
import os
from dotenv import load_dotenv

# Load env config to get Telegram details for crash alerts
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

TG_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TG_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

def tg_alert(text):
    if not TG_TOKEN or not TG_CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    try:
        requests.post(url, json={
            "chat_id": TG_CHAT_ID, "text": text, "parse_mode": "Markdown"
        }, timeout=10)
    except Exception:
        pass

def run_agent():
    agent_path = os.path.join(BASE_DIR, "agent.py")
    print(f"[*] Supervisor: Starting agent at {agent_path}")
    tg_alert("⚠️ *Supervisor:* Starting/Rebooting your Autonomous AI Agent...")
    
    # Run agent.py as a subprocess, piping output so we can see it
    proc = subprocess.Popen([sys.executable, agent_path], stdout=None, stderr=None)
    
    # Wait for the subprocess to exit
    exit_code = proc.wait()
    print(f"[!] Supervisor: Agent terminated with exit code {exit_code}")
    tg_alert(f"🚨 *Supervisor Warning:* Your AI Agent crashed or terminated with exit code `{exit_code}`. Restarting in 10 seconds...")
    time.sleep(10)

def main():
    print("═" * 60)
    print("  AUTONOMOUS AGENT MONITOR SUPERVISOR — Starting up...")
    print("═" * 60)
    while True:
        try:
            run_agent()
        except KeyboardInterrupt:
            print("\n[-] Supervisor terminated by user.")
            sys.exit(0)
        except Exception as e:
            print(f"[-] Supervisor encountered error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    main()
