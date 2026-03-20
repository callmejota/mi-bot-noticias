from flask import Flask, render_template_string
from supabase.client import create_client

# --- TUS CREDENCIALES ---
URL = "https://tkeramrwcqykyapvygzb.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRrZXJhbXJ3Y3F5a3lhcHZ5Z3piIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM5MDc1OTcsImV4cCI6MjA4OTQ4MzU5N30.FMu0ZsJ5A1ljPQYLuM5Nc8KM5VoXlkHbzY6eApBln2g"

supabase = create_client(URL, KEY)

app = Flask(__name__)

# --- EL ARREGLO ESTÁ AQUÍ EN EL HTML (Corchetes en vez de puntos) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Dipi Bot Noticias</title>
    <style>
        body { font-family: sans-serif; background-color: #121212; color: white; padding: 40px; }
        .noticia { background: #1e1e1e; padding: 20px; border-radius: 10px; margin-bottom: 20px; border-left: 5px solid #00d1b2; }
        a { color: #00d1b2; text-decoration: none; font-weight: bold; }
    </style>
</head>
<body>
    <h1>Noticias de DP 🤖</h1>
    {% for noticia in noticias %}
    <div class="noticia">
        <h3>{{ noticia['titulo'] }}</h3>
        <a href="{{ noticia['url'] }}" target="_blank">Leer noticia →</a>
    </div>
    {% endfor %}
</body>
</html>
"""

@app.route('/')
def home():
    try:
        # Buscamos las noticias
        res = supabase.table("noticias").select("*").execute()
        
        # Extraemos la lista
        if hasattr(res, 'data'):
            noticias = res.data
        elif isinstance(res, dict) and 'data' in res:
            noticias = res['data']
        else:
            noticias = res
            
        return render_template_string(HTML_TEMPLATE, noticias=noticias)
    except Exception as e:
        return f"Error en la web: {e}"

if __name__ == '__main__':
    app.run(debug=True)