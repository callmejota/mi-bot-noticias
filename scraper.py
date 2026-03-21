import os
import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from supabase import create_client

# 1. Configuración de Conexiones
URL = os.environ.get("SUPABASE_URL")
KEY = os.environ.get("SUPABASE_KEY")
supabase = create_client(URL, KEY)

# 2. Configuración de Búsquedas
TEMAS = {
    "Nieve ❄️": "Niseko Hirafu snow report OR skiing news when:1d",
    "Cripto 💰": "bitcoin ethereum precio noticias español when:1d",
    "Fútbol ⚽": "Selección Argentina Messi partidos hoy when:1d"
}

# --- FUNCIONES DE DATOS ---

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

# ¡FUNCIÓN MEJORADA: Salta el escudo de Google y lee la noticia real!
def extraer_primer_parrafo(url_google):
    try:
        # Nos disfrazamos de navegador de PC para que no nos bloqueen
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'}
        session = requests.Session()
        
        # 1. Entramos al link escudo de Google
        res = session.get(url_google, headers=headers, timeout=8)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 2. Buscamos la URL REAL que Google esconde en el código
        url_real = url_google
        for meta in soup.find_all('meta'):
            if meta.get('http-equiv', '').lower() == 'refresh':
                url_real = meta['content'].split('url=')[-1].strip("'\"")
                break
        
        # Si no lo escondió en el meta tag, buscamos el link principal
        if url_real == url_google:
            a_tag = soup.find('a')
            if a_tag and a_tag.get('href'):
                url_real = a_tag['href']

        # Si por alguna razón seguimos atrapados en Google, cancelamos
        if 'news.google.com' in url_real:
            return "Haz clic en el título para leer el desarrollo de la noticia."

        # 3. Entramos a la web REAL del diario (Ej: Infobae, ESPN)
        res_diario = session.get(url_real, headers=headers, timeout=8)
        soup_diario = BeautifulSoup(res_diario.text, 'html.parser')
        
        # 4. Leemos los textos y nos quedamos con el primer párrafo grande
        for p in soup_diario.find_all('p'):
            texto = p.get_text().strip()
            if len(texto) > 100: # Si tiene más de 100 letras, seguro es el resumen
                return texto[:220] + "..."
                
        return "Haz clic en el título para leer el desarrollo de la noticia."
    except:
        return "Haz clic en el título para leer el desarrollo de la noticia."

# --------------------------

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
            
            for item in root.findall('.//item')[:2]:
                titulo_completo = item.find('title').text
                titulo = titulo_completo.split(" - ")[0]
                link = item.find('link').text
                
                fuente_tag = item.find('source')
                fuente = fuente_tag.text if fuente_tag is not None else "Diario"

                # ¡Ahora el bot usa el súper-lector!
                parrafo = extraer_primer_parrafo(link)

                try:
                    supabase.table("noticias").insert({"titulo": titulo, "url": link, "categoria": categoria}).execute()
                except:
                    pass
                
                cuerpo_mensaje += f"• <b><a href='{link}'>{titulo}</a></b>\n"
                cuerpo_mensaje += f"📰 <i>{fuente}</i>: {parrafo}\n\n"
        except Exception as e:
            cuerpo_mensaje += "• <i>Error cargando noticias.</i>\n\n"

    cuerpo_mensaje += "⚡ <i>Información procesada para DP</i>"
    enviar_telegram(cuerpo_mensaje)

if __name__ == "__main__":
    buscar_y_guardar()