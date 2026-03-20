import os
import requests
import xml.etree.ElementTree as ET
from supabase import create_client

# --- CONFIGURACIÓN DE LLAVES ---
URL = os.environ.get("SUPABASE_URL")
KEY = os.environ.get("SUPABASE_KEY")

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
        supabase.table("noticias").delete().neq("id", 0).execute()
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

if __name__ == "__main__":
    buscar_y_guardar()