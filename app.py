import os
from flask import Flask, render_template_string
from supabase import create_client

app = Flask(__name__)

# --- CONFIGURACIÓN DE LLAVES ---
URL = os.environ.get("SUPABASE_URL") or "https://tkeramrwcqykyapvygzb.supabase.co"
KEY = os.environ.get("SUPABASE_KEY") or "TeyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRrZXJhbXJ3Y3F5a3lhcHZ5Z3piIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM5MDc1OTcsImV4cCI6MjA4OTQ4MzU5N30.FMu0ZsJ5A1ljPQYLuM5Nc8KM5VoXlkHbzY6eApBln2g"
supabase = create_client(URL, KEY)

HTML_LAYOUT = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Dipi Hub 🤖</title>
    <style>
        body { background-color: #121212; color: white; font-family: 'Segoe UI', sans-serif; padding: 40px; }
        h1 { text-align: center; color: #00d1b2; }
        .categoria-titulo { 
            border-bottom: 2px solid #00d1b2; 
            margin-top: 40px; 
            padding-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 2px;
        }
        .contenedor-noticias { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-top: 20px; }
        .card { background: #1e1e1e; padding: 20px; border-left: 5px solid #00d1b2; border-radius: 8px; }
        a { color: #00d1b2; text-decoration: none; font-weight: bold; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <h1>Noticias de DP 🤖</h1>

    {% if not categorias %}
        <p style="text-align:center;">Todavía no hay noticias. ¡Corre el scraper!</p>
    {% endif %}

    {% for nombre_cat, lista in categorias.items() %}
        <h2 class="categoria-titulo">{{ nombre_cat }}</h2>
        <div class="contenedor-noticias">
            {% for noticia in lista %}
                <div class="card">
                    <p>{{ noticia.titulo }}</p>
                    <a href="{{ noticia.url }}" target="_blank">Leer noticia →</a>
                </div>
            {% endfor %}
        </div>
    {% endfor %}
</body>
</html>
"""

@app.route('/')
def home():
    try:
        # Traemos todas las noticias de Supabase
        res = supabase.table("noticias").select("*").execute()
        datos = res.data
        
        # Las agrupamos por categoría en un diccionario
        noticias_por_cat = {}
        for n in datos:
            cat = n.get('categoria', 'General')
            if cat not in noticias_por_cat:
                noticias_por_cat[cat] = []
            noticias_por_cat[cat].append(n)
            
        return render_template_string(HTML_LAYOUT, categorias=noticias_por_cat)
    except Exception as e:
        return f"Error en la web: {e}"

if __name__ == '__main__':
    app.run(debug=True)