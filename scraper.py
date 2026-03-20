import os
import requests  # <--- ESTA ES LA QUE FALTA
import xml.etree.ElementTree as ET
from supabase import create_client

# ... resto del código ...

URL = os.environ.get("SUPABASE_URL") or "https://tkeramrwcqykyapvygzb.supabase.co"
KEY = os.environ.get("SUPABASE_KEY") or "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRrZXJhbXJ3Y3F5a3lhcHZ5Z3piIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM5MDc1OTcsImV4cCI6MjA4OTQ4MzU5N30.FMu0ZsJ5A1ljPQYLuM5Nc8KM5VoXlkHbzY6eApBln2g"

supabase = create_client(URL, KEY)

# Definimos los temas que te interesan
TEMAS = {
    "Nieve": "Esquí Niseko Hokkaido nieve",
    "Cripto": "Bitcoin Ethereum criptomonedas",
    "Fútbol": "Resultados fútbol Argentina Messi"
}

def buscar_y_guardar():
    for categoria, busqueda in TEMAS.items():
        print(f"Buscando {categoria}...")
        url_rss = f"https://news.google.com/rss/search?q={busqueda}&hl=es-419&gl=US&ceid=US:es-419"
        
        try:
            respuesta = requests.get(url_rss)
            root = ET.fromstring(respuesta.text)
            
            for item in root.findall('.//item')[:3]: # 3 noticias por categoría
                data = {
                    "titulo": item.find('title').text,
                    "url": item.find('link').text,
                    "categoria": categoria # <--- Guardamos la categoría
                }
                supabase.table("noticias").insert(data).execute()
                print(f"✅ [{categoria}] Guardado")
        except Exception as e:
            print(f"❌ Error en {categoria}: {e}")

if __name__ == "__main__":
    buscar_y_guardar()