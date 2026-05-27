# Ficha Técnica — Plataforma MITA

**Multi-Intercultural-Transdisciplina Analógica**  
Gobierno del Estado de México · SEDESA · Versión 1.0.0 · Mayo 2026

---

## Identificación

| Campo | Valor |
|-------|-------|
| Nombre | Plataforma MITA |
| Entidad | Gobierno del Estado de México — SEDESA |
| Proyecto referencia | EDOMEX DIABETES 2026–2032 |
| Requisitos base | RF-01 a RF-11 (`mita.docx`) |

## Stack

| Componente | Tecnología |
|------------|------------|
| Backend | Python 3.11+, Django 5.x |
| API | Django REST Framework 3.15 |
| BD desarrollo | SQLite |
| BD producción | PostgreSQL (vía `DATABASE_URL`) |
| PDF | ReportLab |
| Frontend | Django Templates, CSS, Leaflet.js |

## Apps Django

`core` · `mita_engine` · `conocimiento` · `geoespacial` · `interculturalidad` · `sni` · `legislacion` · `proyectos` · `reportes` · `api`

## Usuarios demo

| Usuario | Rol | Contraseña |
|---------|-----|------------|
| `dependencia` | Dependencia Gubernamental | `mita2026` |
| `analista` | Analista MITA | `mita2026` |
| `investigador` | Investigador SNI | `mita2026` |
| `admin` | Administrador | `mita2026` |
| `auditor` | Auditor (solo lectura) | `mita2026` |

Expedientes demo: `MITA-DEMO-2026-ACTIVO` (paso 6) · `MITA-DEMO-2026-DICTAMINADO`

---

## Comandos para correr el sistema

### Instalación (Windows)

```powershell
cd "c:\Users\rocio\OneDrive\Documents\GitHub\MI"
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_mita
python manage.py check
```

### Servidor de desarrollo

```powershell
# Puerto 8000 (por defecto)
python manage.py runserver

# Puerto alternativo
python manage.py runserver 127.0.0.1:8888
```

**Acceso:** http://127.0.0.1:8000/login/

### Mantenimiento

```powershell
python manage.py seed_mita              # Recargar datos demo
python manage.py createsuperuser        # Nuevo admin
python manage.py test                   # Pruebas
python manage.py collectstatic --noinput  # Estáticos (prod)
```

### Regenerar manual con pantallas

```powershell
python scripts/capturar_pantallas_manual.py
python scripts/generar_manual_docx.py
```

### Producción

```powershell
set DJANGO_DEBUG=False
set DJANGO_SECRET_KEY=clave-segura-generada
set DATABASE_URL=postgres://usuario:clave@host:5432/mita
set DJANGO_ALLOWED_HOSTS=midominio.gob.mx

python manage.py migrate
python manage.py collectstatic --noinput
gunicorn mita_platform.wsgi:application --bind 0.0.0.0:8000
```

### Linux / macOS

```bash
cd MI
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_mita
python manage.py runserver 0.0.0.0:8000
```

---

## Variables de entorno

| Variable | Uso |
|----------|-----|
| `DJANGO_SECRET_KEY` | Clave secreta |
| `DJANGO_DEBUG` | `True` / `False` |
| `DJANGO_ALLOWED_HOSTS` | Hosts permitidos |
| `DATABASE_URL` | Activa PostgreSQL |
| `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` | Conexión PostgreSQL |

---

## Documentación

- Ficha técnica HTML: `docs/FICHA_TECNICA_MITA.html`
- Manual de usuario: `docs/manual-usuario/MANUAL_USUARIO_MITA.html`
- README: `README.md`
