import os
import requests
import xml.etree.ElementTree as ET
from supabase.client import create_client

URL = os.environ.get("SUPABASE_URL")
KEY = os.environ.get("SUPABASE_KEY")
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