import feedparser
import json
import os
import time
import re
from datetime import datetime
from pathlib import Path

# ============================================================
#  CONFIGURACION
# ============================================================
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
OUTPUT_DIR = Path("docs")
MAX_ARTICULOS = 12  # Artículos en portada

# Fuentes RSS de fútbol en español
FUENTES_RSS = [
    {"nombre": "Marca",   "url": "https://www.marca.com/rss/portada.xml"},
    {"nombre": "AS",      "url": "https://as.com/rss/tags/futbol.xml"},
    {"nombre": "Sport",   "url": "https://www.sport.es/rss/portada.xml"},
]
# ============================================================


def obtener_noticias():
    """Obtiene noticias de los feeds RSS."""
    noticias = []
    for fuente in FUENTES_RSS:
        try:
            feed = feedparser.parse(fuente["url"])
            for entry in feed.entries[:5]:
                noticias.append({
                    "titulo":  entry.get("title", ""),
                    "resumen": entry.get("summary", entry.get("description", ""))[:500],
                    "link":    entry.get("link", ""),
                    "fecha":   entry.get("published", datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000")),
                    "fuente":  fuente["nombre"],
                })
        except Exception as e:
            print(f"  ⚠️  Error leyendo {fuente['nombre']}: {e}")

    print(f"  📰 {len(noticias)} noticias obtenidas")
    return noticias[:MAX_ARTICULOS]


def reescribir_con_ia(titulo, resumen):
    """Reescribe el artículo usando Claude AI."""
    if not ANTHROPIC_API_KEY:
        # Sin API key, usamos el resumen original
        return resumen

    try:
        import urllib.request
        import urllib.error

        prompt = f"""Eres un redactor deportivo experto en fútbol español e internacional.
Reescribe esta noticia de fútbol en español de forma original, atractiva y diferente al original.
Usa un tono dinámico y apasionado. Máximo 3 párrafos cortos.
NO copies literalmente el texto original.

Título: {titulo}
Resumen original: {resumen}

Escribe solo el artículo reescrito, sin títulos ni comentarios extra."""

        data = json.dumps({
            "model": "claude-haiku-4-5-20251001",
            "max_tokens": 400,
            "messages": [{"role": "user", "content": prompt}]
        }).encode("utf-8")

        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=data,
            headers={
                "Content-Type": "application/json",
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01"
            }
        )

        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode())
            return result["content"][0]["text"]

    except Exception as e:
        print(f"  ⚠️  Error con IA: {e}")
        return resumen


def limpiar_html(texto):
    """Elimina etiquetas HTML del texto."""
    return re.sub(r'<[^>]+>', '', texto).strip()


def formatear_fecha(fecha_str):
    """Formatea la fecha para mostrar."""
    try:
        import email.utils
        fecha = email.utils.parsedate_to_datetime(fecha_str)
        meses = ["ene","feb","mar","abr","may","jun","jul","ago","sep","oct","nov","dic"]
        return f"{fecha.day} {meses[fecha.month-1]} {fecha.year}"
    except:
        return datetime.now().strftime("%d/%m/%Y")


def generar_card(noticia, idx):
    """Genera el HTML de una tarjeta de noticia."""
    titulo   = limpiar_html(noticia["titulo"])
    contenido = limpiar_html(noticia["contenido"])
    fecha    = formatear_fecha(noticia["fecha"])
    fuente   = noticia["fuente"]
    link     = noticia["link"]

    # Primera card más grande
    if idx == 0:
        return f"""
    <article class="card card--featured" style="animation-delay: 0s">
      <div class="card__tag">{fuente}</div>
      <h2 class="card__title card__title--big">{titulo}</h2>
      <p class="card__body">{contenido[:350]}...</p>
      <div class="card__footer">
        <span class="card__date">📅 {fecha}</span>
        <a href="{link}" target="_blank" rel="noopener" class="card__link">Leer más →</a>
      </div>
    </article>"""

    return f"""
    <article class="card" style="animation-delay: {idx * 0.08}s">
      <div class="card__tag">{fuente}</div>
      <h3 class="card__title">{titulo}</h3>
      <p class="card__body">{contenido[:180]}...</p>
      <div class="card__footer">
        <span class="card__date">📅 {fecha}</span>
        <a href="{link}" target="_blank" rel="noopener" class="card__link">Leer →</a>
      </div>
    </article>"""


def generar_html(noticias):
    """Genera el HTML completo del blog."""
    hora_actualizacion = datetime.now().strftime("%d/%m/%Y a las %H:%M")
    cards_html = "\n".join([generar_card(n, i) for i, n in enumerate(noticias)])

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>GolDigital — Noticias de Fútbol</title>
  <meta name="description" content="Las últimas noticias de fútbol español e internacional. Actualizado automáticamente.">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@400;500;700&display=swap" rel="stylesheet">

  <!-- GOOGLE ADSENSE — reemplaza con tu código real -->
  <!-- <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-XXXXXXXXXX" crossorigin="anonymous"></script> -->

  <style>
    :root {{
      --verde:   #00FF87;
      --negro:   #0a0a0a;
      --gris1:   #111111;
      --gris2:   #1a1a1a;
      --gris3:   #2a2a2a;
      --blanco:  #f0f0f0;
      --texto:   #b0b0b0;
    }}

    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

    body {{
      background: var(--negro);
      color: var(--blanco);
      font-family: 'DM Sans', sans-serif;
      min-height: 100vh;
    }}

    /* HEADER */
    header {{
      background: var(--gris1);
      border-bottom: 2px solid var(--verde);
      padding: 0 24px;
      position: sticky;
      top: 0;
      z-index: 100;
    }}
    .header-inner {{
      max-width: 1100px;
      margin: 0 auto;
      display: flex;
      align-items: center;
      justify-content: space-between;
      height: 64px;
    }}
    .logo {{
      font-family: 'Bebas Neue', sans-serif;
      font-size: 32px;
      letter-spacing: 3px;
      color: var(--blanco);
    }}
    .logo span {{ color: var(--verde); }}
    .update-badge {{
      font-size: 11px;
      color: var(--verde);
      letter-spacing: 1px;
      border: 1px solid var(--verde)44;
      padding: 4px 10px;
      border-radius: 20px;
      background: var(--verde)11;
    }}

    /* HERO BANNER ADSENSE */
    .ad-banner {{
      background: var(--gris2);
      border-bottom: 1px solid var(--gris3);
      text-align: center;
      padding: 12px;
      font-size: 11px;
      color: #444;
      letter-spacing: 2px;
    }}

    /* MAIN */
    main {{
      max-width: 1100px;
      margin: 0 auto;
      padding: 40px 24px;
    }}

    .section-title {{
      font-family: 'Bebas Neue', sans-serif;
      font-size: 14px;
      letter-spacing: 4px;
      color: var(--verde);
      margin-bottom: 24px;
      display: flex;
      align-items: center;
      gap: 12px;
    }}
    .section-title::after {{
      content: '';
      flex: 1;
      height: 1px;
      background: var(--gris3);
    }}

    /* GRID */
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
      gap: 20px;
    }}

    /* CARDS */
    @keyframes fadeUp {{
      from {{ opacity: 0; transform: translateY(20px); }}
      to   {{ opacity: 1; transform: translateY(0); }}
    }}

    .card {{
      background: var(--gris1);
      border: 1px solid var(--gris3);
      border-radius: 8px;
      padding: 24px;
      transition: border-color 0.2s, transform 0.2s;
      animation: fadeUp 0.5s ease both;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }}
    .card:hover {{
      border-color: var(--verde)66;
      transform: translateY(-3px);
    }}
    .card--featured {{
      grid-column: 1 / -1;
      border-color: var(--verde)44;
      background: linear-gradient(135deg, var(--gris1), var(--gris2));
    }}

    .card__tag {{
      display: inline-block;
      font-size: 10px;
      font-weight: 700;
      letter-spacing: 2px;
      text-transform: uppercase;
      color: var(--verde);
      background: var(--verde)15;
      border: 1px solid var(--verde)33;
      padding: 3px 10px;
      border-radius: 20px;
      width: fit-content;
    }}
    .card__title {{
      font-family: 'DM Sans', sans-serif;
      font-weight: 700;
      color: var(--blanco);
      line-height: 1.3;
      font-size: 16px;
    }}
    .card__title--big {{ font-size: 22px; }}
    .card__body {{
      color: var(--texto);
      font-size: 14px;
      line-height: 1.7;
      flex: 1;
    }}
    .card__footer {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-top: auto;
      padding-top: 12px;
      border-top: 1px solid var(--gris3);
    }}
    .card__date {{
      font-size: 12px;
      color: #444;
    }}
    .card__link {{
      font-size: 12px;
      font-weight: 700;
      color: var(--verde);
      text-decoration: none;
      letter-spacing: 1px;
      transition: opacity 0.2s;
    }}
    .card__link:hover {{ opacity: 0.7; }}

    /* AD LATERAL */
    .ad-sidebar {{
      background: var(--gris2);
      border: 1px dashed var(--gris3);
      border-radius: 8px;
      padding: 20px;
      text-align: center;
      font-size: 11px;
      color: #333;
      letter-spacing: 2px;
      min-height: 250px;
      display: flex;
      align-items: center;
      justify-content: center;
    }}

    /* FOOTER */
    footer {{
      background: var(--gris1);
      border-top: 1px solid var(--gris3);
      text-align: center;
      padding: 24px;
      margin-top: 60px;
      font-size: 12px;
      color: #333;
      letter-spacing: 1px;
    }}
    footer span {{ color: var(--verde); }}

    @media (max-width: 600px) {{
      .card--featured {{ grid-column: 1; }}
      .logo {{ font-size: 24px; }}
    }}
  </style>
</head>
<body>

  <header>
    <div class="header-inner">
      <div class="logo">GOL<span>DIGITAL</span></div>
      <div class="update-badge">⚡ Actualizado: {hora_actualizacion}</div>
    </div>
  </header>

  <!-- Banner publicitario superior (AdSense) -->
  <div class="ad-banner">
    PUBLICIDAD &nbsp;·&nbsp; ADSENSE BANNER 728x90
    <!-- ins class="adsbygoogle" ... -->
  </div>

  <main>
    <div class="section-title">⚽ ÚLTIMAS NOTICIAS</div>

    <div class="grid">
{cards_html}

      <!-- Bloque AdSense dentro del grid -->
      <div class="ad-sidebar">
        ADSENSE<br>300x250
        <!-- ins class="adsbygoogle" ... -->
      </div>
    </div>
  </main>

  <footer>
    <p>© 2026 <span>GolDigital</span> — Noticias generadas automáticamente con IA</p>
    <p style="margin-top:8px;">Fuentes: Marca · AS · Sport</p>
  </footer>

</body>
</html>"""


def main():
    print()
    print("  ╔══════════════════════════════════════╗")
    print("  ║       GENERADOR BLOG FUTBOL          ║")
    print("  ╚══════════════════════════════════════╝\n")

    OUTPUT_DIR.mkdir(exist_ok=True)

    # 1. Obtener noticias
    print("  📡 Obteniendo noticias RSS...")
    noticias_raw = obtener_noticias()

    if not noticias_raw:
        print("  ❌ No se pudieron obtener noticias.")
        return

    # 2. Reescribir con IA
    print("  🤖 Reescribiendo con IA...")
    noticias = []
    for i, n in enumerate(noticias_raw):
        print(f"     [{i+1}/{len(noticias_raw)}] {n['titulo'][:50]}...")
        contenido = reescribir_con_ia(n["titulo"], limpiar_html(n["resumen"]))
        noticias.append({**n, "contenido": contenido})
        time.sleep(0.5)  # Pausa para no saturar la API

    # 3. Generar HTML
    print("  🎨 Generando HTML...")
    html = generar_html(noticias)
    output_file = OUTPUT_DIR / "index.html"
    output_file.write_text(html, encoding="utf-8")

    print(f"  ✅ Blog generado: {output_file}")
    print(f"  📊 {len(noticias)} artículos publicados\n")


if __name__ == "__main__":
    main()
