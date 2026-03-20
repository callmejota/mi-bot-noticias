import os
import requests
import xml.etree.ElementTree as ET
from supabase import create_client

# 1. Conexión a Supabase
URL = os.environ.get("SUPABASE_URL")
KEY = os.environ.get("SUPABASE_KEY")
supabase = create_client(URL, KEY)

# 2. Función de Telegram (Ahora con DEBUG real)
def enviar_telegram(mensaje):
    token = os.environ.get("TELEGRAM_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    print(f"DEBUG: Intentando enviar a ID {chat_id}")
    
    if token and chat_id:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {"chat_id": chat_id, "text": mensaje, "parse_mode": "HTML"}
        r = requests.post(url, json=payload)
        print(f"RESPUESTA TELEGRAM: {r.status_code} - {r.text}")
    else:
        print("❌ ERROR: Faltan llaves en GitHub Secrets")

# 3. Función Principal
def buscar_y_guardar():
    TEMAS = {
        "Nieve ❄️": "Esquiar en Niseko Hokkaido nieve",
        "Cripto 💰": "Precio Bitcoin Ethereum noticias",
        "Fútbol ⚽": "Selección Argentina Messi partidos"
    }

    # Limpiar noticias viejas
    try:
        supabase.table("noticias").delete().neq("id", 0).execute()
    except Exception as e:
        print(f"Aviso: No se pudo limpiar la tabla: {e}")

    for categoria, busqueda in TEMAS.items():
        print(f"Buscando {categoria}...")
        url_rss = f"https://news.google.com/rss/search?q={busqueda}&hl=es-419&gl=US&ceid=US:es-419"
        res = requests.get(url_rss)
        root = ET.fromstring(res.text)
        
        for item in root.findall('.//item')[:3]:
            data = {"titulo": item.find('title').text, "url": item.find('link').text, "categoria": categoria}
            supabase.table("noticias").insert(data).execute()
            print(f"✅ Guardado en {categoria}")

    print("Iniciando envío de Telegram...")
    enviar_telegram("🚀 <b>¡Dipi Hub Actualizado!</b>\nNoticias frescas en: https://mi-bot-noticias.vercel.app/")

if __name__ == "__main__":
    buscar_y_guardar()