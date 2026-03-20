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
def enviar_telegram(mensaje):
    token = os.environ.get("TELEGRAM_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if token and chat_id:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        # Usamos disable_web_page_preview para que no se llene de fotos de links
        payload = {
            "chat_id": chat_id, 
            "text": mensaje, 
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }
        requests.post(url, json=payload)

def buscar_y_guardar():
    # Iniciamos el mensaje con la fecha de hoy
    cuerpo_mensaje = "<b>🗞️ RESUMEN DE NOTICIAS DIARIO</b>\n\n"

    for categoria, busqueda in TEMAS.items():
        cuerpo_mensaje += f"<b>{categoria}:</b>\n"
        print(f"Buscando {categoria}...")
        
        url_rss = f"https://news.google.com/rss/search?q={busqueda}&hl=es-419&gl=US&ceid=US:es-419"
        res = requests.get(url_rss)
        root = ET.fromstring(res.text)
        
        # Agarramos las 3 más importantes
        for item in root.findall('.//item')[:3]:
            titulo = item.find('title').text
            link = item.find('link').text
            
            # Guardar en Supabase (como antes)
            data = {"titulo": titulo, "url": link, "categoria": categoria}
            supabase.table("noticias").insert(data).execute()
            
            # AGREGAR AL MENSAJE DE TELEGRAM
            # Cortamos el título si es muy largo para que no sea un choclo
            resumen_titulo = (titulo[:75] + '...') if len(titulo) > 75 else titulo
            cuerpo_mensaje += f"• <a href='{link}'>{resumen_titulo}</a>\n"
        
        cuerpo_mensaje += "\n" # Espacio entre categorías

    cuerpo_mensaje += "<i>Actualizado desde Dipi Ski Club ❄️</i>"

    print("Enviando resumen detallado a Telegram...")
    enviar_telegram(cuerpo_mensaje)