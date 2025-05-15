import time
import requests
import schedule
from datetime import datetime
import os

os.environ['NO_PROXY'] = 'localhost,127.0.0.1'

API_URL = "http://localhost:5000/send_notification"
TIMEOUT_SECONDS = 10

def log(msg, level="INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{level}] {timestamp} - {msg}")

def api_disponivel():
    try:
        response = requests.post(API_URL, timeout=TIMEOUT_SECONDS)
        if response.status_code == 200:
            log("API está disponível.")
            return True
        else:
            log(f"API respondeu com status {response.status_code}, tentando novamente...", "WARN")
            return False
    except requests.exceptions.RequestException as e:
        log(f"Erro ao conectar com a API: {e}", "ERRO")
        return False

def job():
    try:
        response = requests.post(API_URL)
        log(f"Notificação disparada. Status: {response.status_code}")
    except Exception as e:
        log(f"Erro durante o envio da notificação: {e}", "ERRO")

# Verifica a disponibilidade antes de iniciar a rotina
log("⏱️ Rotina de notificações iniciada.")
if not api_disponivel():
    log("Não foi possível iniciar a rotina porque a API não está disponível.", "ERRO")
    exit(1)

# Agendamento
schedule.every(5).minutes.do(job)
log("A rotina está agendada para rodar a cada 5 minutos.")

# Loop principal
while True:
    schedule.run_pending()
    time.sleep(1)
