# ⚽ GolDigital — Blog de Fútbol Automático

Blog de noticias de fútbol generado automáticamente con IA, listo para monetizar con Google AdSense.

---

## 🚀 Cómo ponerlo en marcha (paso a paso)

### 1. Crear cuenta en GitHub
- Ve a https://github.com y crea una cuenta gratis
- Crea un nuevo repositorio llamado `goldigital`
- Marca la opción **"Public"**

### 2. Subir los archivos
Sube estos archivos a tu repositorio:
```
generar_blog.py
.github/workflows/actualizar.yml
```

### 3. Activar GitHub Pages
- Ve a tu repositorio → **Settings** → **Pages**
- En "Source" selecciona **Deploy from a branch**
- Branch: `main`, carpeta: `/docs`
- Guarda. Tu web estará en: `https://TU_USUARIO.github.io/goldigital`

### 4. Añadir API Key de Claude (opcional pero recomendado)
Para que la IA reescriba los artículos:
- Ve a https://console.anthropic.com y crea una API key
- En tu repositorio GitHub → **Settings** → **Secrets** → **Actions**
- Añade un secreto llamado `ANTHROPIC_API_KEY` con tu key

### 5. Lanzar por primera vez
- Ve a **Actions** → **Actualizar Blog de Fútbol** → **Run workflow**
- Espera 1-2 minutos y visita tu web

¡A partir de aquí se actualiza sola cada hora!

---

## 💰 Monetizar con Google AdSense

1. Ve a https://adsense.google.com y solicita una cuenta
2. Añade tu web `https://TU_USUARIO.github.io/goldigital`
3. Cuando te aprueben, edita `generar_blog.py` y reemplaza los comentarios de AdSense con tu código real

---

## 📁 Estructura del proyecto

```
goldigital/
├── generar_blog.py              # Script principal
├── .github/
│   └── workflows/
│       └── actualizar.yml       # Automatización cada hora
└── docs/
    └── index.html               # Web generada (se crea automáticamente)
```

---

## ⚙️ Configuración

En `generar_blog.py` puedes cambiar:

```python
MAX_ARTICULOS = 12      # Número de noticias en portada
INTERVALO     = '0 * * * *'  # Frecuencia (cada hora por defecto)
```
