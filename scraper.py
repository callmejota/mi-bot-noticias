import os
import requests
import xml.etree.ElementTree as ET
from supabase import create_client

# 1. Configuración de llaves
URL = os.environ.get("SUPABASE_URL")
KEY = os.environ.get("SUPABASE_KEY")
supabase = create_client(URL, KEY)

# 2. DEFINICIÓN DE TELEGRAM (IMPORTANTE: VA ARRIBA)
def enviar_telegram(mensaje):
    token = os.environ.get("TELEGRAM_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if token and chat_id:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {"chat_id": chat_id, "text": mensaje, "parse_mode": "HTML"}
        try:
            r = requests.post(url, json=payload)
            print(f"Resultado Telegram: {r.status_code}")
        except Exception as e:
            print(f"Error enviando: {e}")

# 3. PROCESO DE BÚSQUEDA
def enviar_telegram(mensaje):
    token = os.environ.get("TELEGRAM_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    
    print(f"DEBUG: Intentando enviar a ID {chat_id} con Token que empieza en {token[:5] if token else 'NADA'}")
    
    if token and chat_id:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {"chat_id": chat_id, "text": mensaje, "parse_mode": "HTML"}
        r = requests.post(url, json=payload)
        # ESTO ES LO QUE NECESITAMOS VER:
        print(f"RESPUESTA TELEGRAM: {r.status_code} - {r.text}") 
    else:
        print("❌ ERROR: No se encontraron las llaves en los Secrets de GitHub")