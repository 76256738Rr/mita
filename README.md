# Plataforma MITA — Django

**Multi-Intercultural-Transdisciplina Analógica**

Herramienta oficial de gestión del conocimiento y buen gobierno para el Estado de México, desarrollada según el documento de requisitos funcionales (`mita.docx`).

## Requisitos cubiertos

| RF | Módulo | Descripción |
|----|--------|-------------|
| RF-01 | `conocimiento` | Gestión de información validada, fuentes oficiales |
| RF-02 | `conocimiento`, `sni` | Motor multi-interdisciplina, perfiles SNI |
| RF-03 | `mita_engine` | Cruces interdisciplinarios y sinergias |
| RF-04 | `interculturalidad` | Saberes tradicionales, comparador cultural |
| RF-05 | `mita_engine` | Síntesis transdisciplinaria |
| RF-06 | `mita_engine` | Motor analógico y dictámenes PDF |
| RF-07 | `geoespacial` | SIG, hotspots, capas geográficas |
| RF-08 | `mita_engine`, `core` | Flujo proyectos/dictámenes, auditoría |
| RF-09 | API búsqueda | Búsqueda semántica básica |
| RF-10 | `legislacion` | Análisis de impacto normativo |
| RF-11 | `reportes` | Dashboards e indicadores de impacto |

## Flujo de procesos (RF-08)

La plataforma implementa un **motor de workflow** con 7 pasos ejecutables:

1. Definición del asunto
2. Recopilación de conocimiento (disciplinas)
3. Organización y relación (cruce interdisciplinario)
4. Análisis y Analogía
5. Generación de opciones
6. Evaluación y selección
7. Dictamen de Validación + seguimiento

### Rutas principales

| Ruta | Descripción |
|------|-------------|
| `/bandeja/` | Bandeja de tareas pendientes |
| `/expedientes/` | Listado de expedientes |
| `/expedientes/nuevo/` | Registrar nuevo caso |
| `/expedientes/<id>/` | Gestión paso a paso con stepper |

### API de workflow

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/expedientes/` | GET/POST | Listar / crear expediente |
| `/api/expedientes/<id>/` | GET | Detalle + historial |
| `/api/expedientes/<id>/avanzar/` | POST | Avanzar al siguiente paso |
| `/api/expedientes/<id>/paso/` | POST | Guardar datos del paso |
| `/api/bandeja/` | GET | Tareas pendientes |

### Usuarios demo

| Usuario | Contraseña | Rol |
|---------|------------|-----|
| dependencia | mita2026 | Dependencia Gubernamental |
| analista | mita2026 | Analista MITA |
| investigador | mita2026 | Investigador SNI |
| admin | mita2026 | Administrador |
| auditor | mita2026 | Auditor (solo lectura) |
| ciudadano | mita2026 | Público General — Ventanilla Ciudadana |

Expedientes demo: `MITA-DEMO-2026-ACTIVO` · `MITA-DEMO-2026-DICTAMINADO` · Reporte: `MITA-CIU-DEMO-00001`

## Documentación

| Documento | Ubicación |
|-----------|-----------|
| Ficha técnica (HTML) | `docs/FICHA_TECNICA_MITA.html` |
| Ficha técnica (Markdown) | `docs/FICHA_TECNICA_MITA.md` |
| Manual de usuario | `docs/manual-usuario/MANUAL_USUARIO_MITA.html` |

## Instalación y ejecución

```powershell
cd MI
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_mita
python manage.py check
python manage.py runserver
```

Abrir: http://127.0.0.1:8000/login/

Si el puerto 8000 está ocupado:

```powershell
python manage.py runserver 127.0.0.1:8888
```

**Admin Django:** http://127.0.0.1:8000/admin/ — usuario `admin` / `mita2026`

## API REST

Base URL: `/api/`

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/health/` | GET | Estado del servicio |
| `/api/dashboard/` | GET | Estadísticas generales |
| `/api/disciplinas/` | GET | Listado de disciplinas |
| `/api/geoespacial/zonas/` | GET | Zonas geográficas |
| `/api/mita/ejes/` | GET | 5 ejes MITA |
| `/api/mita/cruce/` | POST | Cruce interdisciplinario |
| `/api/mita/analogia/` | POST | Evaluación analógica |
| `/api/mita/dictamen/` | POST | Generar dictamen + PDF |
| `/api/buscar/?q=` | GET | Búsqueda semántica |
| `/api/reportes/indicadores/` | GET | Indicadores de impacto |

## Estructura

```
MI/
├── mita_platform/     # Configuración Django
├── core/              # Usuarios, auditoría, vistas web
├── conocimiento/      # Disciplinas y fuentes (RF-01)
├── geoespacial/       # SIG y mapas (RF-07)
├── mita_engine/       # Motor MITA, dictámenes (RF-03–06)
├── proyectos/         # Proyectos y lecciones aprendidas
├── sni/               # Perfiles investigadores SNI
├── interculturalidad/ # Saberes tradicionales (RF-04)
├── legislacion/       # Impacto normativo (RF-10)
├── reportes/          # Indicadores (RF-11)
├── api/               # REST API
├── templates/         # Interfaz web
└── static/            # CSS
```

## Stack

- **Backend:** Python 3.11+, Django 5, Django REST Framework
- **Base de datos:** SQLite (desarrollo) / PostgreSQL (producción vía `DATABASE_URL`)
- **PDF:** ReportLab para Dictámenes MITA
- **Mapas:** Leaflet.js

## Producción

```bash
set DJANGO_DEBUG=False
set DJANGO_SECRET_KEY=clave-segura
set DATABASE_URL=postgres://user:pass@host:5432/mita
python manage.py collectstatic
gunicorn mita_platform.wsgi:application
```
