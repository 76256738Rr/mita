"""Genera el manual de usuario MITA en formato Word (.docx)."""

from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt, RGBColor

BASE = Path(__file__).resolve().parent.parent
OUT = BASE / 'docs' / 'manual-usuario' / 'MANUAL_USUARIO_MITA.docx'
IMG = BASE / 'docs' / 'manual-usuario' / 'pantallas'


def add_heading(doc, text, level=1):
    h = doc.add_heading(text, level=level)
    for run in h.runs:
        run.font.color.rgb = RGBColor(26, 54, 93)
    return h


def add_figure(doc, image_name, caption):
    path = IMG / image_name
    if path.exists():
        doc.add_picture(str(path), width=Inches(6.2))
        p = doc.add_paragraph(caption)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for run in p.runs:
            run.font.size = Pt(9)
            run.font.italic = True
            run.font.color.rgb = RGBColor(113, 128, 150)
    doc.add_paragraph()


def main():
    doc = Document()
    style = doc.styles['Normal']
    style.font.name = 'Calibri'
    style.font.size = Pt(11)

    title = doc.add_heading('Manual de Usuario', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub = doc.add_paragraph('Plataforma MITA\nMulti-Intercultural-Transdisciplina Analógica')
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    meta = doc.add_paragraph(
        'Gobierno del Estado de México — SEDESA\n'
        'Versión 1.0 · Mayo 2026\n'
        'Proyecto de referencia: EDOMEX DIABETES 2026–2032'
    )
    meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_page_break()

    add_heading(doc, '1. Introducción')
    doc.add_paragraph(
        'La Plataforma MITA es la herramienta oficial de gestión del conocimiento y buen gobierno '
        'del Estado de México. Integra bases interdisciplinarias, análisis geoespacial, evaluación '
        'analógica, perfiles SNI y emisión de dictámenes en un flujo de 7 pasos.'
    )
    doc.add_paragraph(
        'El entorno demo incluye el proyecto simulado EDOMEX DIABETES 2026–2032 con expedientes '
        'precargados para practicar el flujo completo.'
    )

    add_heading(doc, '2. Acceso al sistema', 1)
    doc.add_paragraph(
        'Abra la URL de la plataforma. En el entorno demo, seleccione una tarjeta de rol en la '
        'pantalla de login. Contraseña para todos los usuarios demo: mita2026.'
    )
    add_figure(doc, '01-login.png', 'Figura 1 — Inicio de sesión por rol')

    add_heading(doc, '3. Roles y permisos', 1)
    table = doc.add_table(rows=6, cols=4)
    table.style = 'Table Grid'
    headers = ['Usuario', 'Rol', 'Responsabilidad', 'Pantalla inicial']
    for i, h in enumerate(headers):
        table.rows[0].cells[i].text = h
    rows = [
        ('dependencia', 'Dependencia Gubernamental', 'Paso 1 — Registro', 'Nuevo expediente'),
        ('analista', 'Analista MITA', 'Pasos 2–5 — Análisis', 'Expediente demo activo'),
        ('investigador', 'Investigador SNI', 'Paso 6 — Selección', 'Expediente demo activo'),
        ('admin', 'Administrador', 'Paso 7 — Dictamen', 'Expediente demo activo'),
        ('auditor', 'Auditor', 'Consulta (solo lectura)', 'Expediente dictaminado'),
    ]
    for r, row in enumerate(rows, 1):
        for c, val in enumerate(row):
            table.rows[r].cells[c].text = val

    add_heading(doc, '4. Dashboard y bandeja', 1)
    add_figure(doc, '02-dashboard.png', 'Figura 2 — Panel de control')
    add_figure(doc, '03-bandeja.png', 'Figura 3 — Bandeja de trabajo')

    add_heading(doc, '5. Proceso operativo', 1)
    doc.add_paragraph(
        'El flujo MITA consta de 7 pasos: Definición → Recopilación → Organización → '
        'Analogía → Opciones → Evaluación SNI → Dictamen.'
    )
    add_figure(doc, '08-proceso-operativo.png', 'Figura 4 — Vista kanban del proceso operativo')

    add_heading(doc, '6. Expedientes', 1)
    add_figure(doc, '04-expedientes.png', 'Figura 5 — Listado de expedientes')
    add_figure(doc, '05-expediente-nuevo.png', 'Figura 6 — Nuevo expediente (Paso 1)')
    add_figure(doc, '06-expediente-paso6.png', 'Figura 7 — Expediente demo en Paso 6')
    add_figure(doc, '07-expediente-dictaminado.png', 'Figura 8 — Expediente dictaminado (auditoría)')

    add_heading(doc, '7. Módulos', 1)
    add_figure(doc, '09-base-conocimiento.png', 'Figura 9 — Base de Conocimiento')
    add_figure(doc, '10-mapa-geoespacial.png', 'Figura 10 — Mapa geoespacial')
    add_figure(doc, '11-metodologia.png', 'Figura 11 — Metodología MITA')
    add_figure(doc, '12-proyecto-demo.png', 'Figura 12 — Proyecto EDOMEX DIABETES')
    add_figure(doc, '13-perfiles-sni.png', 'Figura 13 — Perfiles SNI')

    add_heading(doc, '8. Dictámenes y reportes', 1)
    add_figure(doc, '14-dictamenes.png', 'Figura 14 — Dictámenes de validación')
    add_figure(doc, '15-reportes.png', 'Figura 15 — Reportes e indicadores')

    add_heading(doc, '9. Recorrido demo sugerido', 1)
    steps = [
        'Entrar como dependencia y revisar el registro de expediente.',
        'Entrar como analista y explorar el expediente MITA-DEMO-2026-ACTIVO.',
        'Entrar como investigador, seleccionar opción y avanzar al Paso 7.',
        'Entrar como admin y emitir el Dictamen de Validación MITA.',
        'Entrar como auditor y consultar MITA-DEMO-2026-DICTAMINADO y reportes.',
    ]
    for i, s in enumerate(steps, 1):
        doc.add_paragraph(f'{i}. {s}', style='List Number')

    add_heading(doc, '10. Preguntas frecuentes', 1)
    faqs = [
        ('¿No puedo editar un expediente?', 'Verifique su rol. El auditor solo consulta.'),
        ('¿Cómo avanzo de paso?', 'Complete los campos, guarde y pulse Avanzar al siguiente paso.'),
        ('¿Cómo reinicio el demo?', 'Ejecute: python manage.py seed_mita'),
    ]
    for q, a in faqs:
        p = doc.add_paragraph()
        p.add_run(q + ' ').bold = True
        p.add_run(a)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(OUT))
    print(f'Manual Word generado: {OUT}')


if __name__ == '__main__':
    main()
