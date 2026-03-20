@app.route('/')
def home():
    try:
        res = supabase.table("noticias").select("*").execute()
        todas = res.data if hasattr(res, 'data') else res
        
        # Organizamos las noticias en un diccionario por categoría
        noticias_por_cat = {}
        for n in todas:
            cat = n.get('categoria', 'General')
            if cat not in noticias_por_cat:
                noticias_por_cat[cat] = []
            noticias_por_cat[cat].append(n)
            
        return render_template_string(HTML_MULTI_CAT, categorias=noticias_por_cat)
    except Exception as e:
        return f"Error: {e}"

# El HTML ahora necesita un bucle doble (uno para categorías, otro para noticias)
HTML_MULTI_CAT = """
...
<body>
    <h1>Dipi Hub 🤖</h1>
    {% for nombre_cat, lista in categorias.items() %}
        <h2 style="color: #00d1b2; border-bottom: 1px solid #333;">{{ nombre_cat }}</h2>
        {% for noticia in lista %}
            <div class="noticia">
                <h3>{{ noticia['titulo'] }}</h3>
                <a href="{{ noticia['url'] }}" target="_blank">Leer más →</a>
            </div>
        {% endfor %}
    {% endfor %}
</body>
...
"""