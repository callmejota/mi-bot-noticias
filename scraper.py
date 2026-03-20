import os
import requests
import xml.etree.ElementTree as ET
from supabase import create_client

# --- CONFIGURACIÓN DE LLAVES ---
URL = "https://tkeramrwcqykyapvygzb.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRrZXJhbXJ3Y3F5a3lhcHZ5Z3piIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM5MDc1OTcsImV4cCI6MjA4OTQ4MzU5N30.FMu0ZsJ5A1ljPQYLuM5Nc8KM5VoXlkHbzY6eApBln2g"

# Conexión a la base de datos
supabase = create_client(URL, KEY)

# Temas con emojis para que la web se vea de diez
TEMAS = {
    "Nieve ❄️": "Esquiar en Niseko Hokkaido nieve",
    "Cripto 💰": "Precio Bitcoin Ethereum noticias",
    "Fútbol ⚽": "Selección Argentina Messi partidos"
}

def buscar_y_guardar():
    # Limpiamos noticias viejas para que no se mezclen con las nuevas sin categoría
    try:
        supabase.table("noticias").insert(data).execute()
    except:
        pass

    for categoria, busqueda in TEMAS.items():
        print(f"Buscando noticias de {categoria}...")
        url_rss = f"https://news.google.com/rss/search?q={busqueda}&hl=es-419&gl=US&ceid=US:es-419"
        
        try:
            respuesta = requests.get(url_rss)
            root = ET.fromstring(respuesta.text)
            
            for item in root.findall('.//item')[:3]:
                data = {
                    "titulo": item.find('title').text,
                    "url": item.find('link').text,
                    "categoria": categoria
                }
                supabase.table("noticias").insert(data).execute()
                print(f"✅ Guardado en {categoria}")
        except Exception as e:
            print(f"❌ Error en {categoria}: {e}")

def buscar_y_guardar():
    # ... (acá está todo tu código que ya funciona) ...
    
    for categoria, busqueda in TEMAS.items():
        # ... (acá busca las noticias) ...
        print(f"✅ Guardado en {categoria}")

    # --- ESTO ES LO NUEVO ---
    # Asegurate de que esta línea tenga los mismos espacios que el "for" de arriba
    print("Iniciando envío de Telegram...")
    enviar_telegram("🚀 ¡Bot Actualizado!")

if __name__ == "__main__":
    buscar_y_guardar()