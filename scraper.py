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
        # Coordenadas exactas de Niseko Hirafu
        lat, lon = 42.86, 140.70
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,apparent_temperature,weather_code&timezone=Asia%2FTokyo"
        res = requests.get(url).json()
        curr = res['current']
        temp = curr['temperature_2m']
        feels_like = curr['apparent_temperature']
        code = curr['weather_code']
        
        # Traducción simple de códigos de clima
        estados = {0: "Despejado ☀️", 1: "Mayormente despejado 🌤️", 2: "Parcialmente nublado ⛅", 3: "Nublado ☁️", 71: "Nieve ligera ❄️", 73: "Nieve moderada ❄️❄️", 75: "Nevada fuerte 🏔️"}
        estado = estados.get(code, "Nieve/Nubes ❄️")
        
        return f"{estado} | {temp}°C (Sensación: {feels_like}°C)"
    except:
        return "Clima no disponible ️☁️"

def obtener_precio_btc():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
        res = requests.get(url).json()
        precio = res['bitcoin']['usd']
        return f"{precio:,.0f}"
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
        payload = {
            "chat_id": chat_id, 
            "text": mensaje, 
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }
        requests.post(url, json=payload)

def buscar_y_guardar():
    # Obtener toda la info de una
    clima = obtener_clima_hirafu()
    btc = obtener_precio_btc()
    yen = obtener_tipo_cambio()

    # Encabezado Pro
    cuerpo_mensaje = "<b>🏔️ REPORTE NISEKO HIRAFU</b>\n"
    cuerpo_mensaje += f"🌡️ <b>Clima:</b> {clima}\n"
    cuerpo_mensaje += f"💴 <b>USD/JPY:</b> ¥{yen}\n"
    cuerpo_mensaje += f"₿ <b>Bitcoin:</b> ${btc}\n"
    cuerpo_mensaje += "----------------------------\n\n"
    cuerpo_mensaje += "<b>🗞️ RESUMEN DIPI SKI CLUB</b>\n\n"

    # Limpiar Supabase
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
            items = root.findall('.//item')

            if not items:
                cuerpo_mensaje += "• <i>Sin novedades hoy.</i>\n"
            else:
                for item in items[:3]:
                    titulo = item.find('title').text
                    link = item.find('link').text
                    supabase.table("noticias").insert({"titulo": titulo, "url": link, "categoria": categoria}).execute()
                    titulo_corto = titulo.split(" - ")[0]
                    cuerpo_mensaje += f"• <a href='{link}'>{titulo_corto}</a>\n"
        except:
            cuerpo_mensaje += "• <i>Error cargando noticias.</i>\n"
        
        cuerpo_mensaje += "\n"

    cuerpo_mensaje += "⚡ <i>Actualizado para DP en Hokkaido</i>"
    enviar_telegram(cuerpo_mensaje)

if __name__ == "__main__":
    buscar_y_guardar()