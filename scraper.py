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
def buscar_y_guardar():
    TEMAS = {
        "Nieve ❄️": "Esquiar en Niseko Hokkaido nieve",
        "Cripto 💰": "Precio Bitcoin Ethereum noticias",
        "Fútbol ⚽": "Selección Argentina Messi partidos"
    }

    for categoria, busqueda in TEMAS.items():
        print(f"Buscando de {categoria}...")
        url_rss = f"https://news.google.com/rss/search?q={busqueda}&hl=es-419&gl=US&ceid=US:es-419"
        res = requests.get(url_rss)
        root = ET.fromstring(res.text)
        
        for item in root.findall('.//item')[:3]:
            data = {"titulo": item.find('title').text, "url": item.find('link').text, "categoria": categoria}
            supabase.table("noticias").insert(data).execute()
            print(f"✅ Guardado en {categoria}")

    # Ahora sí, el robot ya sabe qué es 'enviar_telegram'
    print("Iniciando envío de Telegram...")
    enviar_telegram("🚀 <b>¡Dipi Hub Actualizado!</b>\nNoticias frescas en: https://mi-bot-noticias.vercel.app/")

if __name__ == "__main__":
    buscar_y_guardar()