import os 
from supabase.client import create_client

URL = os.environ.get("SUPABASE_URL")
KEY = os.environ.get("SUPABASE_KEY")

supabase = create_client(URL, KEY)


def buscar_noticias(tema):
    print(f"Buscando noticias sobre: {tema}...")
    
    # Usamos el canal oficial de noticias de Google (¡No falla!)
    url_rss = f"https://news.google.com/rss/search?q={tema}&hl=es-419&gl=US&ceid=US:es-419"
    
    try:
        respuesta = requests.get(url_rss)
        root = ET.fromstring(respuesta.text)
        
        noticias_encontradas = 0
        
        # Buscamos los primeros 5 artículos
        for item in root.findall('.//item')[:5]:
            titulo = item.find('title').text
            link = item.find('link').text
            
            # Guardamos en Supabase
            data = {"titulo": titulo, "url": link}
            supabase.table("noticias").insert(data).execute()
            print(f"✅ Guardado: {titulo}")
            noticias_encontradas += 1
            
        if noticias_encontradas == 0:
            print("❌ No se encontraron noticias con ese tema.")
            
    except Exception as e:
        print(f"❌ Error buscando noticias: {e}")

if __name__ == "__main__":
    buscar_noticias("Cotización Yen a Dólar")