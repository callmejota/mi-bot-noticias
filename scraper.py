import os
import requests
import xml.etree.ElementTree as ET
from supabase import create_client

# 1. Configuración de Conexiones
URL = os.environ.get("SUPABASE_URL")
KEY = os.environ.get("SUPABASE_KEY")
supabase = create_client(URL, KEY)

# 2. Configuración de Búsquedas (Últimas 24 horas)
TEMAS = {
    "Nieve ❄️": "Niseko Hirafu snow report OR skiing news when:1d",
    "Cripto 💰": "bitcoin ethereum precio noticias español when:1d",
    "Fútbol ⚽": "Selección Argentina Messi partidos hoy when:1d"
}

# --- FUNCIONES DE DATOS EN TIEMPO REAL ---

def obtener_clima_hirafu():
    try:
        lat, lon = 42.86, 140.70
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,apparent_temperature,weather_code&timezone=Asia%2FTokyo"
        res = requests.get(url).json()
        curr = res['current']
        temp, feels, code = curr['temperature_2m'], curr['apparent_temperature'], curr['weather_code']
        estados = {0: "Despejado ☀️", 1: "Mayormente despejado 🌤️", 2: "Parcialmente nublado ⛅", 3: "Nublado ☁️", 71: "Nieve ligera ❄️", 73: "Nieve moderada ❄️❄️", 75: "Nevada fuerte 🏔️"}
        return f"{estados.get(code, 'Nieve/Nubes ❄️')} | {temp}°C (Sensación: {feels}°C)"
    except:
        return "Clima no disponible ☁️"

def obtener_precio_btc():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
        res = requests.get(url).json()
        return f"{res['bitcoin']['usd']:,.0f}"
    except:
        return "N/A"

def obtener_tipo_cambio():
    try:
        url = "https://open.er-api.com/v6/latest/USD"
        res = requests.get(url).json()
        return f"{res['rates']['JPY']:.2f}"
    except:
        return "N/A"

# ---------------------------------------

def enviar_telegram(mensaje):
    token = os.environ.get("TELEGRAM_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if token and chat_id:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {"chat_id": chat_id, "text": mensaje, "parse_mode": "HTML", "disable_web_page_preview": True}
        requests.post(url, json=payload)

def buscar_y_guardar():
    clima, btc, yen = obtener_clima_hirafu(), obtener_precio_btc(), obtener_tipo_cambio()

    cuerpo_mensaje = "<b>🏔️ REPORTE NISEKO HIRAFU</b>\n"
    cuerpo_mensaje += f"🌡️ <b>Clima:</b> {clima}\n"
    cuerpo_mensaje += f"💴 <b>USD/JPY:</b> ¥{yen} | ₿ <b>BTC:</b> ${btc}\n"
    cuerpo_mensaje += "----------------------------\n\n"
    cuerpo_mensaje += "<b>🗞️ RESUMEN DEL DÍA</b>\n\n"

    try:
        supabase.table("noticias").delete().neq("id", 0).execute()
    except:
        pass

    for categoria, busqueda in TEMAS.items():
        cuerpo_mensaje += f"<b>{categoria}:</b>\n"
        url_rss = f"https://news.google.com/rss/search?q={busqueda}&hl=es-419&gl=US&ceid=US:es-419"
        
        try:
            res = requests.get(url_rss)
            root = ET.fromstring(res.text)
            
            for item in root.findall('.//item')[:2]: # Mantenemos 2 noticias para que sea de lectura rápida
                titulo_completo = item.find('title').text
                titulo = titulo_completo.split(" - ")[0]
                link = item.find('link').text
                
                # Buscamos la fuente original (Ej: "Sporting News") de forma limpia
                fuente_tag = item.find('source')
                fuente = fuente_tag.text if fuente_tag is not None else "Diario"

                # Guardamos en la base de datos
                try:
                    supabase.table("noticias").insert({"titulo": titulo, "url": link, "categoria": categoria}).execute()
                except:
                    pass
                
                # Armamos el texto para que quede como un reporte profesional
                cuerpo_mensaje += f"• <b><a href='{link}'>{titulo}</a></b>\n"
                cuerpo_mensaje += f"📰 <i>Fuente: {fuente}</i>\n\n"
        except Exception as e:
            print(f"Error en {categoria}: {e}")
            cuerpo_mensaje += "• <i>Error cargando noticias.</i>\n\n"

    cuerpo_mensaje += "⚡ <i>Información procesada para DP</i>"
    enviar_telegram(cuerpo_mensaje)

if __name__ == "__main__":
    buscar_y_guardar()