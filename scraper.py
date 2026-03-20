import os
import requests
import xml.etree.ElementTree as ET
from supabase import create_client

# 1. Configuración de Clientes
URL = os.environ.get("SUPABASE_URL")
KEY = os.environ.get("SUPABASE_KEY")
supabase = create_client(URL, KEY)

TEMAS = {
    "Nieve ❄️": "Esquiar en Niseko Hokkaido nieve",
    "Cripto 💰": "Precio Bitcoin Ethereum noticias",
    "Fútbol ⚽": "Selección Argentina Messi partidos"
}

# 2. Función de envío a Telegram
def enviar_telegram(mensaje):
    token = os.environ.get("TELEGRAM_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if token and chat_id:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat_id, 
            "text": mensaje, 
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }
        try:
            r = requests.post(url, json=payload)
            print(f"Respuesta Telegram: {r.status_code}")
        except Exception as e:
            print(f"Error envíando Telegram: {e}")

# 3. Función Principal de Búsqueda y Resumen
def buscar_y_guardar():
    # Iniciamos el texto del mensaje
    cuerpo_mensaje = "<b>🗞️ RESUMEN DIARIO DIPI SKI CLUB</b>\n\n"

    # Limpiar noticias viejas en Supabase
    try:
        supabase.table("noticias").delete().neq("id", 0).execute()
    except:
        pass

    for categoria, busqueda in TEMAS.items():
        print(f"Buscando {categoria}...")
        cuerpo_mensaje += f"<b>{categoria}:</b>\n"
        
        url_rss = f"https://news.google.com/rss/search?q={busqueda}&hl=es-419&gl=US&ceid=US:es-419"
        res = requests.get(url_rss)
        root = ET.fromstring(res.text)
        
        # Procesamos las 3 mejores noticias
        for item in root.findall('.//item')[:3]:
            titulo = item.find('title').text
            link = item.find('link').text
            
            # Guardar en Supabase
            try:
                data = {"titulo": titulo, "url": link, "categoria": categoria}
                supabase.table("noticias").insert(data).execute()
            except:
                pass
            
            # Añadir al texto de Telegram con el link en el título
            clean_title = titulo.split(" - ")[0] # Limpiamos el nombre del diario al final
            cuerpo_mensaje += f"• <a href='{link}'>{clean_title}</a>\n"
        
        cuerpo_mensaje += "\n"

    cuerpo_mensaje += "<i>Checkeá la web: https://mi-bot-noticias.vercel.app/</i>"

    print("Enviando resumen a Telegram...")
    enviar_telegram(cuerpo_mensaje)

if __name__ == "__main__":
    buscar_y_guardar()