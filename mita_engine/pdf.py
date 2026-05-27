"""Generación de PDF para Dictámenes MITA."""

import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def generar_pdf_dictamen(dictamen_data):
    """Genera PDF del Dictamen de Validación MITA."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'MITATitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#1a365d'),
        spaceAfter=12,
    )
    heading_style = ParagraphStyle(
        'MITAHeading',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#2c5282'),
        spaceBefore=12,
        spaceAfter=6,
    )
    body_style = ParagraphStyle(
        'MITABody',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
    )

    story = []
    story.append(Paragraph('GOBIERNO DEL ESTADO DE MÉXICO', body_style))
    story.append(Paragraph('DICTAMEN DE VALIDACIÓN MITA', title_style))
    story.append(Spacer(1, 0.3 * cm))

    info_data = [
        ['Folio:', dictamen_data.get('folio', '')],
        ['Fecha:', dictamen_data.get('fecha', '')],
        ['Solicitante:', dictamen_data.get('solicitante', '')],
        ['Asunto:', dictamen_data.get('asunto', '')],
        ['Resultado:', dictamen_data.get('resultado', '')],
        ['Puntuación:', f"{dictamen_data.get('puntuacion', 0)}/100"],
    ]
    info_table = Table(info_data, colWidths=[4 * cm, 12 * cm])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#edf2f7')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 0.5 * cm))

    story.append(Paragraph('Descripción', heading_style))
    story.append(Paragraph(dictamen_data.get('descripcion', ''), body_style))

    story.append(Paragraph('Criterios Evaluados', heading_style))
    criterios = dictamen_data.get('criterios_evaluados', {})
    criterios_data = [['Criterio', 'Puntuación']]
    for nombre, valor in criterios.items():
        criterios_data.append([nombre.replace('_', ' ').title(), f'{valor:.1f}%'])
    criterios_table = Table(criterios_data, colWidths=[10 * cm, 6 * cm])
    criterios_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5282')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    story.append(criterios_table)

    if dictamen_data.get('recomendaciones'):
        story.append(Paragraph('Recomendaciones', heading_style))
        for rec in dictamen_data['recomendaciones']:
            story.append(Paragraph(f'• {rec}', body_style))

    story.append(Spacer(1, 1 * cm))
    story.append(Paragraph(dictamen_data.get('validez', ''), body_style))

    doc.build(story)
    buffer.seek(0)
    return buffer
