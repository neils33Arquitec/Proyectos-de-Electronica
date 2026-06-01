# -*- coding: utf-8 -*-
"""
Generador de Resumen Hiper-Detallado en PDF
Proyecto: Sistema de Llenado de Flujo Continuo con Control Automático
Autor: Neil Edickson Suarez Arevalo (NeilsAraquitec)
Co-Autor: Jose Fabien Salas Garcia
Universidad Santiago Mariño – Teoría Moderna de Control
"""

from reportlab.lib.pagesizes import A4, letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether, ListFlowable, ListItem
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.platypus.flowables import Flowable
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
import datetime
import os

# ────────────────────────────────────────────────────────────────
# PALETA DE COLORES
# ────────────────────────────────────────────────────────────────
AZUL_OSCURO   = HexColor("#0D3B66")
AZUL_MEDIO    = HexColor("#1565C0")
AZUL_CLARO    = HexColor("#1E88E5")
CIAN          = HexColor("#00ACC1")
VERDE         = HexColor("#2E7D32")
NARANJA       = HexColor("#E65100")
GRIS_OSCURO   = HexColor("#212121")
GRIS_MEDIO    = HexColor("#546E7A")
GRIS_CLARO    = HexColor("#ECEFF1")
GRIS_TABLA    = HexColor("#B0BEC5")
BLANCO        = colors.white
NEGRO         = colors.black
AMARILLO_BG   = HexColor("#FFF9C4")
AZUL_BG       = HexColor("#E3F2FD")
VERDE_BG      = HexColor("#E8F5E9")
NARANJA_BG    = HexColor("#FFF3E0")


# ────────────────────────────────────────────────────────────────
# NUMERACIÓN DE PÁGINAS Y ENCABEZADOS
# ────────────────────────────────────────────────────────────────
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        page_num = self._pageNumber
        if page_num == 1:
            return
        w, h = A4
        self.setFont("Helvetica", 8)
        self.setFillColor(GRIS_MEDIO)
        # Línea separadora del pie
        self.setStrokeColor(AZUL_CLARO)
        self.setLineWidth(0.5)
        self.line(2*cm, 1.5*cm, w - 2*cm, 1.5*cm)
        # Pie izquierdo
        self.drawString(2*cm, 1.1*cm,
            "Sistema de Llenado de Flujo Continuo – Teoría Moderna de Control")
        # Pie derecho
        self.drawRightString(w - 2*cm, 1.1*cm,
            f"Página {page_num} de {page_count}")
        # Encabezado
        self.setStrokeColor(AZUL_CLARO)
        self.line(2*cm, h - 1.8*cm, w - 2*cm, h - 1.8*cm)
        self.setFillColor(AZUL_OSCURO)
        self.setFont("Helvetica-Bold", 8)
        self.drawString(2*cm, h - 1.4*cm, "RESUMEN TÉCNICO DEL PROYECTO")
        self.setFont("Helvetica", 8)
        self.setFillColor(GRIS_MEDIO)
        self.drawRightString(w - 2*cm, h - 1.4*cm,
            "Universidad Santiago Mariño  |  2026")


# ────────────────────────────────────────────────────────────────
# ESTILOS
# ────────────────────────────────────────────────────────────────
def build_styles():
    s = getSampleStyleSheet()

    styles = {}

    styles['portada_titulo'] = ParagraphStyle(
        'portada_titulo',
        parent=s['Title'],
        fontSize=26,
        leading=32,
        textColor=BLANCO,
        alignment=TA_CENTER,
        spaceAfter=10,
        fontName='Helvetica-Bold',
    )
    styles['portada_subtitulo'] = ParagraphStyle(
        'portada_subtitulo',
        parent=s['Normal'],
        fontSize=14,
        leading=18,
        textColor=HexColor("#B3E5FC"),
        alignment=TA_CENTER,
        spaceAfter=6,
        fontName='Helvetica',
    )
    styles['portada_info'] = ParagraphStyle(
        'portada_info',
        parent=s['Normal'],
        fontSize=11,
        leading=15,
        textColor=HexColor("#E0F7FA"),
        alignment=TA_CENTER,
        spaceAfter=4,
        fontName='Helvetica',
    )
    styles['h1'] = ParagraphStyle(
        'h1',
        parent=s['Heading1'],
        fontSize=16,
        leading=20,
        textColor=BLANCO,
        spaceAfter=4,
        spaceBefore=18,
        fontName='Helvetica-Bold',
        alignment=TA_LEFT,
        leftIndent=0,
        borderPad=6,
    )
    styles['h2'] = ParagraphStyle(
        'h2',
        parent=s['Heading2'],
        fontSize=13,
        leading=17,
        textColor=AZUL_OSCURO,
        spaceAfter=4,
        spaceBefore=12,
        fontName='Helvetica-Bold',
        borderColor=AZUL_CLARO,
        borderWidth=0,
        leftIndent=0,
    )
    styles['h3'] = ParagraphStyle(
        'h3',
        parent=s['Heading3'],
        fontSize=11,
        leading=14,
        textColor=AZUL_MEDIO,
        spaceAfter=3,
        spaceBefore=8,
        fontName='Helvetica-Bold',
        leftIndent=8,
    )
    styles['body'] = ParagraphStyle(
        'body',
        parent=s['Normal'],
        fontSize=10,
        leading=14,
        textColor=GRIS_OSCURO,
        spaceAfter=5,
        fontName='Helvetica',
        alignment=TA_JUSTIFY,
    )
    styles['body_bold'] = ParagraphStyle(
        'body_bold',
        parent=s['Normal'],
        fontSize=10,
        leading=14,
        textColor=GRIS_OSCURO,
        spaceAfter=4,
        fontName='Helvetica-Bold',
    )
    styles['code'] = ParagraphStyle(
        'code',
        parent=s['Code'],
        fontSize=8.5,
        leading=12,
        textColor=HexColor("#1A237E"),
        fontName='Courier',
        backColor=HexColor("#F5F5F5"),
        leftIndent=12,
        rightIndent=8,
        spaceAfter=4,
        spaceBefore=2,
        borderColor=HexColor("#BDBDBD"),
        borderWidth=0.5,
        borderPad=4,
        borderRadius=2,
    )
    styles['caption'] = ParagraphStyle(
        'caption',
        parent=s['Normal'],
        fontSize=8,
        leading=11,
        textColor=GRIS_MEDIO,
        alignment=TA_CENTER,
        spaceAfter=6,
        fontName='Helvetica-Oblique',
    )
    styles['bullet'] = ParagraphStyle(
        'bullet',
        parent=s['Normal'],
        fontSize=10,
        leading=14,
        textColor=GRIS_OSCURO,
        spaceAfter=3,
        fontName='Helvetica',
        leftIndent=16,
        bulletIndent=6,
    )
    styles['formula'] = ParagraphStyle(
        'formula',
        parent=s['Normal'],
        fontSize=10,
        leading=14,
        textColor=HexColor("#1A237E"),
        fontName='Courier-Bold',
        alignment=TA_CENTER,
        spaceAfter=4,
        spaceBefore=4,
        backColor=AZUL_BG,
        borderColor=AZUL_CLARO,
        borderWidth=0.8,
        borderPad=6,
    )
    styles['alerta'] = ParagraphStyle(
        'alerta',
        parent=s['Normal'],
        fontSize=9.5,
        leading=13,
        textColor=NARANJA,
        fontName='Helvetica-Bold',
        leftIndent=10,
        spaceAfter=4,
    )
    styles['toc_entry'] = ParagraphStyle(
        'toc_entry',
        parent=s['Normal'],
        fontSize=10,
        leading=16,
        textColor=AZUL_MEDIO,
        fontName='Helvetica',
        leftIndent=6,
    )
    styles['toc_sub'] = ParagraphStyle(
        'toc_sub',
        parent=s['Normal'],
        fontSize=9,
        leading=14,
        textColor=GRIS_MEDIO,
        fontName='Helvetica',
        leftIndent=20,
    )
    return styles


# ────────────────────────────────────────────────────────────────
# HELPERS DE CONSTRUCCIÓN
# ────────────────────────────────────────────────────────────────
def section_header(text, number, styles):
    """Retorna una cabecera de sección nivel 1 con fondo de color."""
    data = [[Paragraph(f"{number}.  {text}", styles['h1'])]]
    t = Table(data, colWidths=[17*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), AZUL_OSCURO),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('ROUNDEDCORNERS', [4, 4, 4, 4]),
    ]))
    return t


def subsection_header(text, styles):
    """Cabecera nivel 2 con barra lateral azul."""
    data = [[Paragraph(text, styles['h2'])]]
    t = Table(data, colWidths=[17*cm])
    t.setStyle(TableStyle([
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LINEBEFORE', (0,0), (0,-1), 3, AZUL_CLARO),
        ('BACKGROUND', (0,0), (-1,-1), AZUL_BG),
    ]))
    return t


def info_box(text, styles, color=AZUL_BG, border=AZUL_CLARO):
    """Caja de información destacada."""
    data = [[Paragraph(text, styles['body'])]]
    t = Table(data, colWidths=[17*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), color),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('BOX', (0,0), (-1,-1), 0.8, border),
        ('ROUNDEDCORNERS', [4, 4, 4, 4]),
    ]))
    return t


def make_table(header_row, data_rows, styles, col_widths=None, zebra=True):
    """Tabla con estilo completo."""
    all_data = header_row + data_rows
    if col_widths is None:
        n = len(header_row)
        col_widths = [17*cm / n] * n

    t = Table(all_data, colWidths=col_widths, repeatRows=1)
    ts = [
        ('BACKGROUND', (0, 0), (-1, 0), AZUL_OSCURO),
        ('TEXTCOLOR', (0, 0), (-1, 0), BLANCO),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8.5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [BLANCO, GRIS_CLARO] if zebra else [BLANCO]),
        ('GRID', (0, 0), (-1, -1), 0.4, GRIS_TABLA),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]
    t.setStyle(TableStyle(ts))
    return t


def bullet_list(items, styles):
    """Lista con viñetas."""
    elems = []
    for item in items:
        elems.append(Paragraph(f"• {item}", styles['bullet']))
    return elems


def sp(n=1):
    return Spacer(1, n * 4 * mm)


# ════════════════════════════════════════════════════════════════
# CONSTRUCCIÓN DEL DOCUMENTO
# ════════════════════════════════════════════════════════════════
def build_pdf(output_path):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=2*cm,
        rightMargin=2*cm,
        topMargin=2.5*cm,
        bottomMargin=2.5*cm,
        title="Resumen Técnico – Sistema de Llenado de Flujo Continuo",
        author="Neil Edickson Suarez Arevalo",
        subject="Teoría Moderna de Control – Universidad Santiago Mariño",
        creator="NeilsAraquitec",
    )

    styles = build_styles()
    story = []
    w = A4[0] - 4*cm  # ancho útil

    # ────────────────────────────────────────────────────────────
    # PORTADA
    # ────────────────────────────────────────────────────────────
    # Fondo azul de portada
    portada_bg = Table(
        [[Paragraph("", styles['portada_titulo'])]],
        colWidths=[w], rowHeights=[3*cm]
    )
    portada_bg.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), AZUL_OSCURO)]))

    portada_data = [
        [Paragraph("UNIVERSIDAD SANTIAGO MARIÑO", styles['portada_info'])],
        [Paragraph("Escuela de Ingeniería", styles['portada_info'])],
        [Spacer(1, 1*cm)],
        [Paragraph("TEORÍA MODERNA DE CONTROL", ParagraphStyle(
            'pmod', parent=styles['portada_subtitulo'],
            fontSize=12, textColor=HexColor("#B3E5FC")))],
        [Spacer(1, 0.5*cm)],
        [Paragraph(
            "SISTEMA DE LLENADO DE FLUJO CONTINUO<br/>CON CONTROL AUTOMÁTICO",
            styles['portada_titulo'])],
        [Spacer(1, 0.3*cm)],
        [HRFlowable(width=12*cm, thickness=1.5, color=CIAN, spaceAfter=4)],
        [Paragraph("RESUMEN TÉCNICO HIPER-DETALLADO", ParagraphStyle(
            'rst', parent=styles['portada_subtitulo'],
            fontSize=13, textColor=CIAN, fontName='Helvetica-Bold'))],
        [Spacer(1, 1.5*cm)],
        [Paragraph("Proyecto Segundo – Versión 2.0", styles['portada_info'])],
        [Spacer(1, 0.4*cm)],
        [Paragraph("<b>Autor:</b>  Neil Edickson Suarez Arevalo  (NeilsAraquitec)", styles['portada_info'])],
        [Paragraph("<b>Co-Autor:</b>  Jose Fabien Salas Garcia", styles['portada_info'])],
        [Spacer(1, 0.8*cm)],
        [Paragraph("Junio 2026", styles['portada_info'])],
    ]

    portada_table = Table(portada_data, colWidths=[w])
    portada_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), AZUL_OSCURO),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 20),
        ('RIGHTPADDING', (0,0), (-1,-1), 20),
    ]))
    story.append(portada_table)
    story.append(PageBreak())

    # ────────────────────────────────────────────────────────────
    # RESUMEN EJECUTIVO
    # ────────────────────────────────────────────────────────────
    story.append(section_header("RESUMEN EJECUTIVO", "0", styles))
    story.append(sp(2))
    story.append(Paragraph(
        "El presente documento constituye el resumen técnico hiper-detallado del proyecto "
        "<b>Sistema de Llenado de Flujo Continuo con Control Automático</b>, desarrollado en el "
        "marco de la asignatura <i>Teoría Moderna de Control</i> de la Universidad Santiago Mariño. "
        "El sistema integra dos microcontroladores (Arduino Uno y ESP32), dos sensores de naturaleza "
        "distinta (ultrasónico HC-SR04 y caudalímetro GFS401), dos bombas de agua controladas por "
        "relés, y una interfaz web embebida accesible por WiFi.",
        styles['body']))
    story.append(Paragraph(
        "El objetivo principal es demostrar la aplicación práctica de la teoría moderna de control "
        "sobre una planta real, incluyendo: modelado matemático por funciones de transferencia y "
        "representación en espacio de estados, análisis de controlabilidad y observabilidad, diseño "
        "de controlador óptimo LQR, e implementación de lógica de control por histéresis en hardware "
        "embebido de bajo costo.",
        styles['body']))

    kpi_data = [
        ["Parámetro", "Valor"],
        ["Tiempo de subida (llenado 0 → 80%)", "≈ 60–90 s"],
        ["Sobrepaso", "Mínimo (banda de histéresis)"],
        ["Error en estado estacionario", "0% (sistema tipo 1)"],
        ["Oscilación en estado estable", "±5% (banda histéresis)"],
        ["Frecuencia de muestreo", "1 Hz (serial)  /  5 Hz (HC-SR04)"],
        ["Caudal medio en llenado", "≈ 2.5 L/min"],
        ["Ciclos ON/OFF en transitorio", "5–8 ciclos"],
        ["Cobertura de firmware", "Arduino (194 líneas) + ESP32 (331 líneas)"],
        ["Simulación Python", "3 escenarios, 615 líneas"],
        ["Análisis MATLAB", "116 líneas, Toolbox de Control"],
    ]
    story.append(make_table(kpi_data[0:1], kpi_data[1:], styles,
                            col_widths=[10*cm, 7*cm]))
    story.append(sp(2))
    story.append(PageBreak())

    # ────────────────────────────────────────────────────────────
    # TABLA DE CONTENIDOS
    # ────────────────────────────────────────────────────────────
    story.append(subsection_header("TABLA DE CONTENIDOS", styles))
    story.append(sp())

    toc = [
        ("1.", "Descripción General del Sistema", ""),
        ("2.", "Arquitectura de Hardware", ""),
        ("  2.1", "Microcontroladores", ""),
        ("  2.2", "Sensores", ""),
        ("  2.3", "Actuadores", ""),
        ("  2.4", "Comunicación y Niveles Lógicos", ""),
        ("  2.5", "Configuración de Pines", ""),
        ("3.", "Protocolo de Comunicación", ""),
        ("4.", "Interfaz Web (HMI)", ""),
        ("5.", "Modelado Matemático", ""),
        ("  5.1", "Funciones de Transferencia", ""),
        ("  5.2", "Representación en Espacio de Estados", ""),
        ("  5.3", "Análisis de Controlabilidad y Observabilidad", ""),
        ("  5.4", "Análisis de Estabilidad", ""),
        ("6.", "Algoritmo de Control", ""),
        ("  6.1", "Control por Histéresis (Implementado)", ""),
        ("  6.2", "Control LQR Óptimo (Propuesto)", ""),
        ("7.", "Firmware: Arduino Uno", ""),
        ("8.", "Firmware: ESP32", ""),
        ("9.", "Simulaciones", ""),
        ("  9.1", "Simulación Python (3 Escenarios)", ""),
        ("  9.2", "Script MATLAB / Simulink", ""),
        ("10.", "Parámetros de Calibración", ""),
        ("11.", "Estructura de Documentación", ""),
        ("12.", "Lista de Materiales y Costos", ""),
        ("13.", "Guía de Resolución de Problemas", ""),
        ("14.", "Secuencia de Operación", ""),
        ("15.", "Mejoras Futuras", ""),
        ("16.", "Referencias Bibliográficas", ""),
    ]
    for num, title, page in toc:
        indent = 20 if num.startswith("  ") else 6
        style_key = 'toc_sub' if num.startswith("  ") else 'toc_entry'
        story.append(Paragraph(
            f"{'&nbsp;'*max(0,(len(num)-2)*2)}<b>{num}</b>  {title}",
            ParagraphStyle('tc', parent=styles[style_key], leftIndent=indent)))
    story.append(PageBreak())

    # ════════════════════════════════════════════════════════════
    # SECCIÓN 1 – DESCRIPCIÓN GENERAL
    # ════════════════════════════════════════════════════════════
    story.append(section_header("DESCRIPCIÓN GENERAL DEL SISTEMA", "1", styles))
    story.append(sp(2))
    story.append(info_box(
        "<b>Nombre del Proyecto:</b> Sistema de Llenado de Flujo Continuo con Control Automático  |  "
        "<b>Versión:</b> 2.0  |  <b>Idioma:</b> Español  |  "
        "<b>Fecha:</b> Junio 2026  |  <b>Institución:</b> Universidad Santiago Mariño",
        styles))
    story.append(sp())

    story.append(Paragraph(
        "El sistema controla automáticamente el nivel de llenado de un depósito de agua utilizando "
        "dos microcontroladores que trabajan en red: el <b>Arduino Uno</b> se encarga de toda la "
        "lógica de control, la adquisición de datos de los sensores y la actuación sobre las bombas; "
        "el <b>ESP32</b> actúa como interfaz IoT, publicando un servidor web embebido accesible desde "
        "cualquier dispositivo con navegador en la misma red WiFi.",
        styles['body']))
    story.append(Paragraph(
        "La arquitectura separa claramente las responsabilidades: el control en tiempo real queda "
        "en el Arduino (ciclo de control de 200 ms) y la capa de comunicación/HMI en el ESP32. "
        "Ambos se comunican por UART serie a 9600 baudios, con adaptación de niveles lógicos "
        "(5V Arduino → 3.3V ESP32) mediante divisor de tensión resistivo.",
        styles['body']))

    story.append(subsection_header("Objetivos del Proyecto", styles))
    for obj in [
        "Aplicar la teoría moderna de control (espacio de estados, LQR) sobre una planta física real.",
        "Implementar un sistema embebido de control automático de nivel con sensor ultrasónico.",
        "Integrar medición de caudal mediante caudalímetro GFS401 por conteo de pulsos.",
        "Desarrollar una interfaz HMI web accesible por WiFi sin necesidad de infraestructura externa.",
        "Validar el modelo matemático de la planta mediante simulación Python y análisis MATLAB.",
        "Documentar el proyecto con estándares académicos y reproducibilidad total.",
    ]:
        story.append(Paragraph(f"• {obj}", styles['bullet']))

    story.append(PageBreak())

    # ════════════════════════════════════════════════════════════
    # SECCIÓN 2 – ARQUITECTURA DE HARDWARE
    # ════════════════════════════════════════════════════════════
    story.append(section_header("ARQUITECTURA DE HARDWARE", "2", styles))
    story.append(sp(2))

    # 2.1 Microcontroladores
    story.append(subsection_header("2.1  Microcontroladores", styles))
    story.append(sp())

    mc_data = [
        ["Característica", "Arduino Uno (ATmega328P)", "ESP32-DevKit"],
        ["CPU / Frecuencia", "ATmega328P / 16 MHz", "Xtensa LX6 / 240 MHz"],
        ["Voltaje de operación", "5V", "3.3V"],
        ["Flash / RAM", "32 KB / 2 KB SRAM", "4 MB / 520 KB SRAM"],
        ["GPIO digitales", "14 (6 PWM)", "34"],
        ["ADC", "6 canales (10-bit)", "18 canales (12-bit)"],
        ["Comunicación", "UART, SPI, I2C, USB", "UART, SPI, I2C, WiFi 802.11, BT"],
        ["Modo WiFi", "No integrado", "Access Point (AP) 2.4 GHz"],
        ["Función en el sistema", "Control principal, sensores, relés", "Servidor web, UART bridge"],
    ]
    story.append(make_table(mc_data[0:1], mc_data[1:], styles,
                            col_widths=[5.5*cm, 5.75*cm, 5.75*cm]))
    story.append(sp(2))

    # 2.2 Sensores
    story.append(subsection_header("2.2  Sensores", styles))
    story.append(sp())
    sens_data = [
        ["Característica", "HC-SR04 (Nivel)", "GFS401 (Caudal)"],
        ["Magnitud medida", "Distancia / nivel (%)", "Caudal (L/min)"],
        ["Principio", "Eco ultrasónico (40 kHz)", "Efecto Hall (paletas giratorias)"],
        ["Rango de medición", "2–400 cm", "1–30 L/min"],
        ["Resolución", "0.3 cm", "≈ 0.13 L/min (1 pulso)"],
        ["Factor de calibración", "Distancia → %: configurable", "7.5 pulsos / L/min"],
        ["Voltaje de alimentación", "5V DC", "5V DC"],
        ["Señal de salida", "ECHO (pulso ancho)", "Tren de pulsos digitales"],
        ["Pin Arduino", "TRIG: 9,  ECHO: 8", "Pin 2 (INT0, flanco bajada)"],
        ["Ruido modelado", "Gaussiano σ = 0.4%", "Error de cuantización"],
    ]
    story.append(make_table(sens_data[0:1], sens_data[1:], styles,
                            col_widths=[5.5*cm, 5.75*cm, 5.75*cm]))
    story.append(sp(2))

    # 2.3 Actuadores
    story.append(subsection_header("2.3  Actuadores", styles))
    story.append(sp())
    act_data = [
        ["Componente", "Bomba 1 (Llenado)", "Bomba 2 (Drenaje)"],
        ["Tipo", "Bomba DC sumergible", "Bomba DC sumergible / circulación"],
        ["Voltaje", "5V o 12V DC", "5V o 12V DC"],
        ["Control", "Relé 2 canales (activo LOW)", "Relé 2 canales (activo LOW)"],
        ["Pin Arduino relé", "Pin 6", "Pin 7"],
        ["Estado activo", "Pin LOW → Relé activado → Bomba ON", "Igual"],
        ["Estado inactivo", "Pin HIGH → Relé libre → Bomba OFF", "Igual"],
        ["Función en AUTO", "Controlada automáticamente", "Sin control AUTO (manual)"],
    ]
    story.append(make_table(act_data[0:1], act_data[1:], styles,
                            col_widths=[5.5*cm, 5.75*cm, 5.75*cm]))
    story.append(sp(2))

    # 2.4 Comunicación
    story.append(subsection_header("2.4  Comunicación y Niveles Lógicos", styles))
    story.append(sp())
    story.append(Paragraph(
        "La comunicación bidireccional entre Arduino Uno (5V) y ESP32 (3.3V) se realiza por UART "
        "mediante la librería <b>SoftwareSerial</b> en el Arduino (pines 10 y 11). Como el ESP32 "
        "no tolera señales de 5V en sus GPIO, se implementa un <b>divisor de tensión resistivo</b> "
        "en la línea TX del Arduino (Arduino-TX → ESP32-RX): resistencias R1=10 kΩ y R2=20 kΩ "
        "reducen 5V a 3.3V exactos. La línea opuesta (ESP32-TX → Arduino-RX) no requiere adaptación "
        "ya que el Arduino reconoce 3.3V como nivel lógico alto.",
        styles['body']))

    comm_data = [
        ["Parámetro", "Valor"],
        ["Velocidad", "9600 baudios, 8N1"],
        ["Pines Arduino", "RX=10, TX=11 (SoftwareSerial)"],
        ["Pines ESP32", "RX=GPIO16 (Serial2), TX=GPIO17"],
        ["Adaptación de nivel", "Divisor: R1=10kΩ, R2=20kΩ → 3.33V"],
        ["Período de transmisión", "Cada 1000 ms (T_ENVIO_MS)"],
        ["Timeout ESP32 → Arduino", "5000 ms (detecta desconexión)"],
        ["Debug USB (Arduino)", "115200 baudios (Monitor Serie)"],
    ]
    story.append(make_table(comm_data[0:1], comm_data[1:], styles,
                            col_widths=[8*cm, 9*cm]))
    story.append(sp(2))

    # 2.5 Pines
    story.append(subsection_header("2.5  Configuración Completa de Pines", styles))
    story.append(sp())
    story.append(Paragraph("<b>Arduino Uno:</b>", styles['body_bold']))
    pins_ard = [
        ["Pin", "Función", "Tipo", "Señal / Descripción"],
        ["2", "GFS401", "Input (INT0)", "Pulsos caudalímetro (flanco bajada)"],
        ["6", "Relé Bomba 1", "Output", "Active LOW → Bomba llenado"],
        ["7", "Relé Bomba 2", "Output", "Active LOW → Bomba drenaje"],
        ["8", "HC-SR04 ECHO", "Input", "Pulso de retorno (duración → distancia)"],
        ["9", "HC-SR04 TRIG", "Output", "Pulso de 10 µs para disparar medición"],
        ["10", "SoftwareSerial RX", "Input", "Recibe comandos desde ESP32"],
        ["11", "SoftwareSerial TX", "Output", "Envía estado al ESP32 (→ div. tensión)"],
    ]
    story.append(make_table(pins_ard[0:1], pins_ard[1:], styles,
                            col_widths=[2*cm, 3.5*cm, 3*cm, 8.5*cm]))
    story.append(sp())
    story.append(Paragraph("<b>ESP32 DevKit:</b>", styles['body_bold']))
    pins_esp = [
        ["GPIO", "Función", "Tipo", "Señal / Descripción"],
        ["16", "Serial2 RX", "Input", "Recibe datos de estado desde Arduino"],
        ["17", "Serial2 TX", "Output", "Envía comandos al Arduino"],
    ]
    story.append(make_table(pins_esp[0:1], pins_esp[1:], styles,
                            col_widths=[2*cm, 3.5*cm, 3*cm, 8.5*cm]))
    story.append(PageBreak())

    # ════════════════════════════════════════════════════════════
    # SECCIÓN 3 – PROTOCOLO DE COMUNICACIÓN
    # ════════════════════════════════════════════════════════════
    story.append(section_header("PROTOCOLO DE COMUNICACIÓN", "3", styles))
    story.append(sp(2))

    story.append(Paragraph(
        "Se utiliza un protocolo ASCII propio, orientado a texto, con pares clave:valor separados "
        "por comas y terminados en salto de línea. Esto facilita el depurado visual y la compatibilidad "
        "con el Monitor Serie del Arduino IDE.",
        styles['body']))

    story.append(subsection_header("Trama Arduino → ESP32 (cada 1 s)", styles))
    story.append(sp())
    story.append(Paragraph(
        "<b>Formato:</b>  N:{nivel},Q:{caudal},B1:{bomba1},B2:{bomba2},"
        "SP:{setpoint},M:{modo},A:{alarma}",
        styles['formula']))
    story.append(sp())

    proto_data = [
        ["Campo", "Tipo", "Rango", "Descripción"],
        ["N", "float (1 dec.)", "0.0 – 100.0", "Nivel de llenado (%)"],
        ["Q", "float (2 dec.)", "0.00 – 30.00", "Caudal instantáneo (L/min)"],
        ["B1", "entero", "0 / 1", "Estado Bomba 1 (0=OFF, 1=ON)"],
        ["B2", "entero", "0 / 1", "Estado Bomba 2 (0=OFF, 1=ON)"],
        ["SP", "entero", "0 – 100", "Setpoint activo (%)"],
        ["M", "entero", "0 / 1", "Modo: 0=MANUAL, 1=AUTO"],
        ["A", "entero", "0 / 1", "Alarma: 1=Bomba ON sin caudal"],
    ]
    story.append(make_table(proto_data[0:1], proto_data[1:], styles,
                            col_widths=[2*cm, 3*cm, 3.5*cm, 8.5*cm]))

    story.append(sp(2))
    story.append(Paragraph("<b>Ejemplo de trama real:</b>", styles['body_bold']))
    story.append(Paragraph("N:75.3,Q:2.15,B1:1,B2:0,SP:80,M:1,A:0", styles['code']))

    story.append(subsection_header("Comandos ESP32 → Arduino", styles))
    story.append(sp())
    cmd_data = [
        ["Comando", "Efecto en Arduino", "Ejemplo"],
        ["B1:1 / B1:0", "Bomba 1 ON / OFF (modo MANUAL)", "B1:1"],
        ["B2:1 / B2:0", "Bomba 2 ON / OFF (modo MANUAL)", "B2:0"],
        ["SP:{valor}", "Actualiza setpoint (0–100%)", "SP:65"],
        ["M:1 / M:0", "Cambio a modo AUTO / MANUAL", "M:1"],
    ]
    story.append(make_table(cmd_data[0:1], cmd_data[1:], styles,
                            col_widths=[4*cm, 8*cm, 5*cm]))

    story.append(sp(2))
    story.append(info_box(
        "<b>Respuesta JSON del ESP32 (ruta GET /data):</b><br/>"
        '{ "nivel": 75.3, "caudal": 2.15, "b1": 1, "b2": 0, "sp": 80, "modo": 1, '
        '"alarma": 0, "conexion": 1 }',
        styles, color=VERDE_BG, border=VERDE))
    story.append(PageBreak())

    # ════════════════════════════════════════════════════════════
    # SECCIÓN 4 – INTERFAZ WEB
    # ════════════════════════════════════════════════════════════
    story.append(section_header("INTERFAZ WEB HMI (EMBEDDED HTML/CSS/JS)", "4", styles))
    story.append(sp(2))

    story.append(info_box(
        "<b>Red WiFi:</b>  ESP32-Llenado   |   "
        "<b>Contraseña:</b>  control2026   |   "
        "<b>URL de acceso:</b>  http://192.168.4.1   |   "
        "<b>Protocolo:</b>  HTTP / REST (sin autenticación adicional)",
        styles))
    story.append(sp())

    story.append(Paragraph(
        "La interfaz web está embebida directamente en el firmware del ESP32 como cadena de "
        "texto HTML/CSS/JavaScript almacenada en Flash (PROGMEM). No requiere servidor externo, "
        "tarjeta SD ni acceso a internet. El ESP32 opera en modo <b>Access Point</b>, creando "
        "su propia red WiFi a la que se conecta el dispositivo del operador.",
        styles['body']))

    story.append(subsection_header("Rutas del Servidor HTTP", styles))
    routes_data = [
        ["Método", "Ruta", "Descripción"],
        ["GET", "/", "Sirve la aplicación web completa (HTML+CSS+JS embebido)"],
        ["GET", "/data", "Devuelve JSON con el estado actual del sistema"],
        ["POST", "/cmd", "Recibe comandos de control (B1, B2, SP, M)"],
    ]
    story.append(make_table(routes_data[0:1], routes_data[1:], styles,
                            col_widths=[2.5*cm, 3*cm, 11.5*cm]))
    story.append(sp())

    story.append(subsection_header("Elementos de la Interfaz", styles))
    ui_elements = [
        "<b>Indicador de nivel:</b> Barra animada azul (0–100%) con línea marcadora naranja para el setpoint.",
        "<b>Pantalla de caudal:</b> Valor en L/min actualizado en tiempo real.",
        "<b>Indicadores de estado de bombas:</b> ● (verde) = ON  /  ○ (gris) = OFF.",
        "<b>Botones de control manual:</b> ON/OFF para cada bomba (activos sólo en modo MANUAL).",
        "<b>Slider de setpoint:</b> Ajuste de 0–100%; envía comando SP:{val} al presionar.",
        "<b>Botón AUTO/MANUAL:</b> Cambia el modo de operación (azul=AUTO, naranja=MANUAL).",
        "<b>Estado del sistema:</b> Timestamp verde si hay conexión; rojo si no llegan datos.",
        "<b>Banner de alarma:</b> Aparece en rojo si la Bomba 1 está activa y el caudal es menor al mínimo (falla de bomba o tubería).",
        "<b>Tema visual:</b> Dark mode inspirado en GitHub, fuente monoespaciada, responsive.",
        "<b>Actualización automática:</b> El JavaScript consulta /data cada 1 segundo.",
    ]
    for e in ui_elements:
        story.append(Paragraph(f"• {e}", styles['bullet']))
    story.append(PageBreak())

    # ════════════════════════════════════════════════════════════
    # SECCIÓN 5 – MODELADO MATEMÁTICO
    # ════════════════════════════════════════════════════════════
    story.append(section_header("MODELADO MATEMÁTICO", "5", styles))
    story.append(sp(2))

    # 5.1 Funciones de transferencia
    story.append(subsection_header("5.1  Funciones de Transferencia", styles))
    story.append(sp())

    story.append(Paragraph(
        "La planta se descompone en dos subsistemas en cascada: el sistema bomba+tubería "
        "(dinámica de primer orden con retardo de transporte) y el depósito (integrador puro).",
        styles['body']))

    story.append(Paragraph("Subsistema Bomba + Tubería (primer orden + retardo):", styles['h3']))
    story.append(Paragraph(
        "G_q(s) = K · e^(-Ls) / (τ_q · s + 1)",
        styles['formula']))
    story.append(sp())

    ft_params = [
        ["Parámetro", "Símbolo", "Valor (experimental)", "Descripción"],
        ["Ganancia estática", "K", "2.5 L/min", "Caudal máximo en régimen permanente"],
        ["Constante de tiempo", "τ_q", "3.0 s", "Tiempo de respuesta al 63%"],
        ["Retardo de transporte", "L", "0.8 s", "Retardo tuberías/válvulas"],
    ]
    story.append(make_table(ft_params[0:1], ft_params[1:], styles,
                            col_widths=[4*cm, 3*cm, 4*cm, 6*cm]))
    story.append(sp())

    story.append(Paragraph("Subsistema Depósito (integrador puro):", styles['h3']))
    story.append(Paragraph(
        "G_h(s) = 1 / (A · s)",
        styles['formula']))
    story.append(sp())
    story.append(Paragraph(
        "Donde <b>A</b> = área transversal del depósito en L/cm.  "
        "Valor experimental: A = 0.5 L/cm.",
        styles['body']))

    story.append(Paragraph("Planta completa (lazo abierto):", styles['h3']))
    story.append(Paragraph(
        "G_total(s) = K · e^(-Ls) / [A · s · (τ_q · s + 1)]",
        styles['formula']))
    story.append(sp())
    story.append(info_box(
        "<b>Tipo de sistema:</b>  Tipo 1 (un integrador) → error de estado estacionario nulo "
        "frente a entrada escalón de referencia.  <b>Polos de lazo abierto:</b>  λ₁ = 0 "
        "(integrador), λ₂ = −1/τ_q = −0.333 (estable).  El sistema es marginalmente estable "
        "en lazo abierto.",
        styles, color=AMARILLO_BG, border=NARANJA))
    story.append(sp(2))

    # 5.2 Espacio de estados
    story.append(subsection_header("5.2  Representación en Espacio de Estados", styles))
    story.append(sp())
    story.append(Paragraph(
        "Se define un modelo de estados de orden 2 con las siguientes variables de estado:",
        styles['body']))
    for sv in [
        "<b>x₁ = h</b>: nivel de llenado (%)",
        "<b>x₂ = q</b>: caudal instantáneo (L/min)",
    ]:
        story.append(Paragraph(f"&nbsp;&nbsp;&nbsp;{sv}", styles['bullet']))
    story.append(sp())

    story.append(Paragraph(
        "Las matrices del sistema en forma canónica son:",
        styles['body']))
    story.append(Paragraph(
        "ẋ = A·x + B·u      y = C·x + D·u",
        styles['formula']))
    story.append(sp())
    story.append(Paragraph(
        "A = [  0       1/A  ]      B = [  0    ]      C = [1 0]      D = [0]\n"
        "    [  0    -1/τ_q  ]          [K/τ_q  ]          [0 1]          [0]",
        styles['code']))
    story.append(sp())
    story.append(Paragraph(
        "Con los valores nominales (K=2.5, τ_q=3.0, A=0.5):",
        styles['body']))
    story.append(Paragraph(
        "A = [0      2.0  ]      B = [0     ]",
        styles['code']))
    story.append(Paragraph(
        "    [0   -0.333  ]          [0.833 ]",
        styles['code']))
    story.append(sp(2))

    # 5.3 Controlabilidad / Observabilidad
    story.append(subsection_header("5.3  Análisis de Controlabilidad y Observabilidad", styles))
    story.append(sp())

    story.append(Paragraph("<b>Matriz de controlabilidad:</b>", styles['body_bold']))
    story.append(Paragraph(
        "Mc = [B  AB] =  [  0       2.0·K/τ_q  ]",
        styles['code']))
    story.append(Paragraph(
        "                [K/τ_q    -K/τ_q²     ]",
        styles['code']))
    story.append(Paragraph(
        "det(Mc) = −K²/τ_q² ≠ 0   →   rango = 2   →   SISTEMA COMPLETAMENTE CONTROLABLE ✓",
        styles['code']))
    story.append(sp())

    story.append(Paragraph(
        "<b>Observabilidad:</b> Ambas variables de estado (nivel y caudal) son medidas "
        "directamente por sensores físicos (HC-SR04 y GFS401), por lo que la matriz de "
        "observabilidad tiene rango completo.  SISTEMA COMPLETAMENTE OBSERVABLE ✓",
        styles['body']))
    story.append(sp(2))

    # 5.4 Estabilidad
    story.append(subsection_header("5.4  Análisis de Estabilidad", styles))
    story.append(sp())
    stab_data = [
        ["Aspecto", "Resultado"],
        ["Polos lazo abierto", "λ₁=0 (integrador), λ₂=−0.333 (semiplano izq.)"],
        ["Estabilidad L.A.", "Marginalmente estable (polo en el origen)"],
        ["Estabilidad con control histéresis", "Oscilación acotada (bounded BIBO)"],
        ["Estabilidad con LQR (propuesto)", "Asintóticamente estable (todos los polos L.C. < 0)"],
        ["Criterio de Routh (sin retardo)", "Condiciones cumplidas para K/τ_q > 0"],
        ["Margen de fase (Bode)", "A identificar experimentalmente"],
        ["Rango de incertidumbre K", "K > 0 → controlabilidad mantenida"],
    ]
    story.append(make_table(stab_data[0:1], stab_data[1:], styles,
                            col_widths=[6.5*cm, 10.5*cm]))
    story.append(PageBreak())

    # ════════════════════════════════════════════════════════════
    # SECCIÓN 6 – ALGORITMO DE CONTROL
    # ════════════════════════════════════════════════════════════
    story.append(section_header("ALGORITMO DE CONTROL", "6", styles))
    story.append(sp(2))

    # 6.1 Histéresis
    story.append(subsection_header("6.1  Control por Histéresis (Implementado en Firmware)", styles))
    story.append(sp())
    story.append(Paragraph(
        "La estrategia de control implementada es un controlador ON/OFF con banda de histéresis "
        "(zona muerta). Este esquema evita el «chattering» (conmutaciones rápidas del relé) que "
        "ocurriría con un comparador puro. La lógica se evalúa cada T_CONTROL_MS = 200 ms.",
        styles['body']))

    story.append(Paragraph("Pseudocódigo del algoritmo de control:", styles['h3']))
    story.append(Paragraph(
        "si modo == AUTO:\n"
        "    banda_inf = setpoint - HISTERESIS_PCT   (ej. 80−5 = 75%)\n"
        "    banda_sup = setpoint + HISTERESIS_PCT   (ej. 80+5 = 85%)\n"
        "    si nivel < banda_inf:\n"
        "        setBomba(BOMBA1, ON)    // Activar llenado\n"
        "    sino si nivel > banda_sup:\n"
        "        setBomba(BOMBA1, OFF)   // Detener llenado\n"
        "    // En [banda_inf, banda_sup]: no hacer nada (histéresis)\n"
        "si caudal < CAUDAL_MIN_ALARMA y bomba1==ON:\n"
        "    alarma = true              // Fallo de caudal",
        styles['code']))
    story.append(sp())

    hyst_data = [
        ["Parámetro", "Valor Default", "Efecto de Variación"],
        ["SETPOINT_DEFAULT", "80%", "Nivel objetivo de llenado"],
        ["HISTERESIS_PCT", "5%", "Mayor: menos ciclos, mayor error | Menor: más ciclos, menor error"],
        ["CAUDAL_MIN_ALARMA", "0.5 L/min", "Umbral de detección de fallo de bomba/tubería"],
        ["T_CONTROL_MS", "200 ms", "Frecuencia de evaluación del lazo de control"],
    ]
    story.append(make_table(hyst_data[0:1], hyst_data[1:], styles,
                            col_widths=[4*cm, 3*cm, 10*cm]))
    story.append(sp())
    story.append(info_box(
        "<b>Ventajas:</b> Robusto, simple, no requiere tuning, previene rebose.  "
        "<b>Limitaciones:</b> Oscilación permanente de ±5%, no minimiza esfuerzo de control, "
        "respuesta más lenta que PID/LQR.",
        styles, color=VERDE_BG, border=VERDE))
    story.append(sp(2))

    # 6.2 LQR
    story.append(subsection_header("6.2  Control LQR Óptimo (Diseñado en MATLAB, Propuesto)", styles))
    story.append(sp())
    story.append(Paragraph(
        "El regulador cuadrático lineal (LQR) minimiza el índice de desempeño:",
        styles['body']))
    story.append(Paragraph(
        "J = ∫₀^∞ [xᵀ·Q·x + uᵀ·R·u] dt",
        styles['formula']))
    story.append(sp())

    lqr_data = [
        ["Parámetro", "Valor", "Criterio de Selección"],
        ["Q[1,1] (peso x₁=nivel)", "10", "Penalizar error de nivel fuertemente"],
        ["Q[2,2] (peso x₂=caudal)", "1", "Peso moderado en caudal"],
        ["R (esfuerzo control)", "1", "Balance esfuerzo/desempeño"],
        ["Ganancia óptima K_lqr", "A calcular con MATLAB lqr()", "Solución ecuación Riccati"],
        ["Prealimentación N", "u = -K_lqr·x + N·r", "Elimina error en estado estacionario"],
    ]
    story.append(make_table(lqr_data[0:1], lqr_data[1:], styles,
                            col_widths=[5*cm, 4*cm, 8*cm]))
    story.append(sp())
    story.append(Paragraph(
        "El script MATLAB <i>simulacion_caudal.m</i> calcula automáticamente K_lqr, "
        "verifica la estabilidad del lazo cerrado, y compara la respuesta escalón del "
        "sistema con LQR versus el sistema en lazo abierto.",
        styles['body']))
    story.append(PageBreak())

    # ════════════════════════════════════════════════════════════
    # SECCIÓN 7 – FIRMWARE ARDUINO
    # ════════════════════════════════════════════════════════════
    story.append(section_header("FIRMWARE: ARDUINO UNO (controlador_principal.ino)", "7", styles))
    story.append(sp(2))

    story.append(info_box(
        "<b>Archivo:</b> 04_Firmware/arduino_uno/controlador_principal/controlador_principal.ino  "
        "|  <b>Líneas:</b> 194  |  <b>Configuración:</b> 04_Firmware/arduino_uno/include/config_arduino.h",
        styles))
    story.append(sp())

    story.append(Paragraph(
        "El firmware del Arduino Uno implementa el lazo de control en tiempo real. "
        "Su estructura sigue el patrón de dos temporizadores independientes (timer-based polling) "
        "sin RTOS, ejecutando tareas a intervalos fijos:",
        styles['body']))

    story.append(subsection_header("Funciones Principales", styles))
    funcs = [
        ["Función", "Período", "Descripción"],
        ["setup()", "Una vez", "Configura pines, inicializa comunicaciones, estado inicial"],
        ["loop()", "Continuo", "Dispatcher principal, evalúa temporizadores"],
        ["medirNivel()", "200 ms", "Promedia LECTURAS_PROMEDIO pulsos HC-SR04, convierte a %"],
        ["medirCaudal()", "1000 ms", "Lee contador de pulsos INT0, convierte a L/min"],
        ["ejecutarControl()", "200 ms", "Lógica de histéresis (modo AUTO)"],
        ["setBomba(id, estado)", "On demand", "Actúa sobre relé (pin LOW/HIGH)"],
        ["enviarEstado()", "1000 ms", "Formatea y envía trama serial al ESP32"],
        ["leerComandos()", "Continuo", "Parser de comandos recibidos del ESP32"],
        ["ISR(INT0_vect)", "Por pulso", "Rutina de interrupción: incrementa contador de pulsos"],
    ]
    story.append(make_table(funcs[0:1], funcs[1:], styles,
                            col_widths=[4*cm, 2.5*cm, 10.5*cm]))
    story.append(sp())

    story.append(subsection_header("Detalles de Implementación Críticos", styles))
    impl_details = [
        "<b>Promediado HC-SR04:</b> Se toman LECTURAS_PROMEDIO mediciones y se promedia para "
        "reducir ruido ultrasónico. Si alguna lectura excede el tiempo de timeout, se descarta.",
        "<b>Conteo de pulsos GFS401:</b> Usa la interrupción externa INT0 (flanco de bajada) "
        "para contar pulsos sin pérdida, incluso a frecuencias moderadas. El contador se limpia "
        "en cada ventana de 1 segundo.",
        "<b>Temporizadores no bloqueantes:</b> Se usa millis() para gestión de tiempo en lugar "
        "de delay(), permitiendo ejecución concurrente de múltiples tareas periódicas.",
        "<b>Lógica de histéresis:</b> La condición de histéresis garantiza que no se active ni "
        "desactive la bomba dentro de la banda [SP-H, SP+H], evitando oscilaciones rápidas.",
        "<b>Alarma de caudal:</b> Si la Bomba 1 lleva más de 2 ciclos ON y el caudal sigue "
        "por debajo de CAUDAL_MIN_ALARMA, se marca la bandera de alarma.",
    ]
    for d in impl_details:
        story.append(Paragraph(f"• {d}", styles['bullet']))
    story.append(PageBreak())

    # ════════════════════════════════════════════════════════════
    # SECCIÓN 8 – FIRMWARE ESP32
    # ════════════════════════════════════════════════════════════
    story.append(section_header("FIRMWARE: ESP32 (interfaz_wifi.ino)", "8", styles))
    story.append(sp(2))

    story.append(info_box(
        "<b>Archivo:</b> 04_Firmware/esp32/interfaz_wifi/interfaz_wifi.ino  "
        "|  <b>Líneas:</b> 331  |  <b>Configuración:</b> 04_Firmware/esp32/include/config_esp32.h",
        styles))
    story.append(sp())

    story.append(subsection_header("Arquitectura del Firmware ESP32", styles))
    story.append(Paragraph(
        "El ESP32 implementa un servidor HTTP asíncrono (o síncrono, según versión) sobre WiFi "
        "en modo Access Point (AP). El bucle principal realiza polling de Serial2 para capturar "
        "tramas del Arduino y actualizar el estado global. Las peticiones HTTP son atendidas por "
        "handlers registrados.",
        styles['body']))

    esp32_tasks = [
        ["Tarea / Handler", "Disparador", "Acción"],
        ["setup()", "Boot", "Inicia AP WiFi, Serial2, registra rutas HTTP"],
        ["loop()", "Continuo", "Polling Serial2, watchdog timeout Arduino"],
        ["handleRoot()", "GET /", "Envía HTML+CSS+JS embebido al cliente"],
        ["handleData()", "GET /data", "Serializa estado global a JSON"],
        ["handleCmd()", "POST /cmd", "Parsea comando, reenvía al Arduino por Serial2"],
        ["parseArduinoData()", "Datos en Serial2", "Extrae campos N,Q,B1,B2,SP,M,A"],
        ["checkTimeout()", "Cada iteración loop", "Marca conexion=0 si silencio > 5000 ms"],
    ]
    story.append(make_table(esp32_tasks[0:1], esp32_tasks[1:], styles,
                            col_widths=[4.5*cm, 3.5*cm, 9*cm]))
    story.append(sp())

    story.append(subsection_header("Parámetros de Configuración ESP32", styles))
    esp32_cfg = [
        ["Constante", "Valor", "Descripción"],
        ["WIFI_SSID", '"ESP32-Llenado"', "Nombre de la red WiFi del AP"],
        ["WIFI_PASS", '"control2026"', "Contraseña de acceso"],
        ["AP_IP", "192.168.4.1", "Dirección IP del servidor web"],
        ["SERIAL2_BAUD", "9600", "Velocidad comunicación con Arduino"],
        ["SERIAL2_RX", "GPIO 16", "Pin de recepción"],
        ["SERIAL2_TX", "GPIO 17", "Pin de transmisión"],
        ["TIMEOUT_ARDUINO_MS", "5000", "Tiempo sin datos → 'Sin conexión'"],
    ]
    story.append(make_table(esp32_cfg[0:1], esp32_cfg[1:], styles,
                            col_widths=[4.5*cm, 4*cm, 8.5*cm]))
    story.append(PageBreak())

    # ════════════════════════════════════════════════════════════
    # SECCIÓN 9 – SIMULACIONES
    # ════════════════════════════════════════════════════════════
    story.append(section_header("SIMULACIONES", "9", styles))
    story.append(sp(2))

    # 9.1 Python
    story.append(subsection_header("9.1  Simulación Python (simulacion_sistema_llenado.py)", styles))
    story.append(sp())

    story.append(info_box(
        "<b>Archivo:</b> 05_Simulaciones/simulacion_sistema_llenado.py  "
        "|  <b>Líneas:</b> 615  |  <b>Requiere:</b> Python 3.7+, numpy, matplotlib",
        styles))
    story.append(sp())

    story.append(Paragraph(
        "El simulador es una réplica exacta del firmware del Arduino Uno más un modelo físico "
        "del sistema hidráulico. Esto permite validar la lógica de control antes de desplegar "
        "en hardware y obtener métricas de desempeño bajo condiciones controladas.",
        styles['body']))

    story.append(subsection_header("Modelo Físico Implementado", styles))
    for m in [
        "<b>Dinámica del caudal (primer orden):</b>  dq/dt = (K·u − q) / τ_q",
        "<b>Dinámica del nivel (integrador):</b>  dh/dt = q / A",
        "<b>Ruido sensor HC-SR04:</b>  h_medido = h + Gaussiano(μ=0, σ=0.4%)",
        "<b>Cuantización GFS401:</b>  Error de cuantización por conteo entero de pulsos",
        "<b>Paso de integración:</b>  dt = 0.05 s (Euler hacia adelante)",
    ]:
        story.append(Paragraph(f"• {m}", styles['bullet']))
    story.append(sp())

    story.append(subsection_header("Tres Escenarios de Validación", styles))
    scenarios = [
        ["#", "Nombre", "Condición Inicial", "Eventos", "Duración"],
        ["1", "Arranque desde cero",
         "h=0%, q=0, SP=80%",
         "Solo llenado automático hasta régimen",
         "350 s"],
        ["2", "Tanque lleno – drenaje",
         "h=100%, q=0, SP=40%",
         "SP cambia, drenaje manual activado",
         "120 s"],
        ["3", "Perturbación externa",
         "h=70%, SP=70%",
         "Drenaje súbito + recuperación + cambio SP",
         "200 s"],
    ]
    story.append(make_table(scenarios[0:1], scenarios[1:], styles,
                            col_widths=[1*cm, 3.5*cm, 3.5*cm, 5.5*cm, 2.5*cm]))
    story.append(sp())

    story.append(subsection_header("Salidas del Simulador", styles))
    for s_out in [
        "Salida de consola con formato ANSI de colores (emula Monitor Serie del Arduino IDE).",
        "Reporte estadístico: tiempo de subida, sobrepaso, número de ciclos bomba, alarmas.",
        "Gráfica matplotlib de 4 paneles: nivel(%), caudal(L/min), estado bomba, alarmas.",
        "Imagen guardada como <i>simulacion_resultado.png</i> en 05_Simulaciones/.",
    ]:
        story.append(Paragraph(f"• {s_out}", styles['bullet']))
    story.append(sp(2))

    # 9.2 MATLAB
    story.append(subsection_header("9.2  Script MATLAB (simulacion_caudal.m)", styles))
    story.append(sp())

    story.append(info_box(
        "<b>Archivo:</b> 05_Simulaciones/MATLAB_Simulink/simulacion_caudal.m  "
        "|  <b>Líneas:</b> 116  |  <b>Requiere:</b> MATLAB R2023+ + Control System Toolbox",
        styles))
    story.append(sp())

    matlab_sections = [
        ["Sección", "Contenido"],
        ["1. Definición de TF", "G_bomba(s), G_tanque(s), G_planta(s) con retardo"],
        ["2. Espacio de estados", "Matrices A, B, C, D con parámetros nominales"],
        ["3. Controlabilidad/Observabilidad", "rank(ctrb(A,B)), rank(obsv(A,C))"],
        ["4. Análisis L.A.", "step(), bode(), rlocus() de G_planta"],
        ["5. Diseño LQR", "K_lqr = lqr(A, B, Q, R); polos lazo cerrado"],
        ["6. Comparación L.C.", "step() lazo abierto vs cerrado con LQR"],
    ]
    story.append(make_table(matlab_sections[0:1], matlab_sections[1:], styles,
                            col_widths=[4.5*cm, 12.5*cm]))
    story.append(PageBreak())

    # ════════════════════════════════════════════════════════════
    # SECCIÓN 10 – PARÁMETROS DE CALIBRACIÓN
    # ════════════════════════════════════════════════════════════
    story.append(section_header("PARÁMETROS DE CALIBRACIÓN", "10", styles))
    story.append(sp(2))

    story.append(Paragraph(
        "Todos los parámetros ajustables por el usuario se centralizan en "
        "<b>04_Firmware/arduino_uno/include/config_arduino.h</b>.  "
        "Modificar este archivo y recompilar permite adaptar el sistema a cualquier "
        "depósito o sensor sin tocar la lógica de control.",
        styles['body']))
    story.append(sp())

    cal_data = [
        ["Constante", "Tipo", "Default", "Rango", "Descripción y Procedimiento de Ajuste"],
        ["MAX_DIST_CM", "float", "30.0", "10–50 cm",
         "Distancia HC-SR04 con depósito vacío. Medir con cinta métrica."],
        ["LECTURAS_PROMEDIO", "int", "3", "1–10",
         "Mediciones a promediar. Aumentar si ruido es alto."],
        ["HISTERESIS_PCT", "float", "5.0", "1–20 %",
         "Semi-banda de histéresis. Compromiso ruido/oscilación."],
        ["SETPOINT_DEFAULT", "int", "80", "0–100 %",
         "Nivel objetivo al iniciar. Sobreescrito por slider web."],
        ["CAUDAL_MIN_ALARMA", "float", "0.5", "0.1–2.0 L/min",
         "Mínimo para alarma. Medir caudal con bomba recién arrancada."],
        ["FACTOR_CAL_GFS401", "float", "7.5", "6–10 pulsos/L/min",
         "Del datasheet. Calibrar con recipiente graduado."],
        ["T_CONTROL_MS", "int", "200", "100–1000 ms",
         "Período del lazo HC-SR04. Menor = más reactivo."],
        ["T_ENVIO_MS", "int", "1000", "500–5000 ms",
         "Período de transmisión serial y medición de caudal."],
    ]
    story.append(make_table(cal_data[0:1], cal_data[1:], styles,
                            col_widths=[4*cm, 1.5*cm, 2*cm, 2.5*cm, 7*cm]))
    story.append(PageBreak())

    # ════════════════════════════════════════════════════════════
    # SECCIÓN 11 – ESTRUCTURA DE DOCUMENTACIÓN
    # ════════════════════════════════════════════════════════════
    story.append(section_header("ESTRUCTURA DE DOCUMENTACIÓN DEL PROYECTO", "11", styles))
    story.append(sp(2))

    struct_data = [
        ["Carpeta / Archivo", "Estado", "Contenido"],
        ["README.md", "✓ Completo", "Visión general, inicio rápido, arquitectura"],
        ["01_Documentacion/Especificaciones_Tecnicas/", "✓ Completo",
         "Especificaciones técnicas detalladas de todos los componentes"],
        ["01_Documentacion/Manual_Usuario/manual_usuario.md", "✓ Completo",
         "Guía de operación para el usuario final (≈80 páginas)"],
        ["01_Documentacion/Manual_Usuario/manual_tecnico_armado.md", "✓ Completo",
         "Guía de ensamblaje y resolución de problemas (347 líneas)"],
        ["01_Documentacion/Informe_Final/", "⚠ Vacío", "Informe académico final (pendiente)"],
        ["01_Documentacion/Presentacion/", "⚠ Vacío", "Diapositivas de presentación (pendiente)"],
        ["02_Modelado_Matematico/Funcion_de_Transferencia/", "✓ Completo",
         "Notas de modelado, procedimiento de identificación"],
        ["02_Modelado_Matematico/Espacio_de_Estados/", "✓ Completo",
         "Formulación espacio de estados, diseño LQR"],
        ["02_Modelado_Matematico/Analisis_de_Estabilidad/", "⚠ Vacío",
         "Análisis formal de estabilidad (pendiente)"],
        ["03_Diseno_del_Sistema/Diagrama_de_Bloques/", "⚠ Vacío",
         "Diagramas de bloques del sistema (pendiente)"],
        ["03_Diseno_del_Sistema/Esquematicos/", "⚠ Vacío",
         "Esquemas eléctricos (pendiente)"],
        ["04_Firmware/arduino_uno/", "✓ Completo",
         "Firmware principal + header de configuración"],
        ["04_Firmware/esp32/", "✓ Completo",
         "Servidor web WiFi + header de configuración"],
        ["05_Simulaciones/simulacion_sistema_llenado.py", "✓ Completo",
         "Simulador Python de 615 líneas, 3 escenarios"],
        ["05_Simulaciones/MATLAB_Simulink/simulacion_caudal.m", "✓ Completo",
         "Script MATLAB 116 líneas, análisis completo"],
        ["06_Resultados_y_Pruebas/Datos_Medicion/", "✓ Plantilla",
         "Formato CSV para registro experimental"],
        ["07_Evidencias/", "⚠ Vacío",
         "Fotos y videos del montaje (pendiente)"],
        ["08_Referencias/referencias.md", "✓ Completo",
         "Bibliografía y enlaces técnicos"],
    ]
    story.append(make_table(struct_data[0:1], struct_data[1:], styles,
                            col_widths=[6.5*cm, 2*cm, 8.5*cm]))
    story.append(PageBreak())

    # ════════════════════════════════════════════════════════════
    # SECCIÓN 12 – LISTA DE MATERIALES
    # ════════════════════════════════════════════════════════════
    story.append(section_header("LISTA DE MATERIALES Y COSTOS ESTIMADOS", "12", styles))
    story.append(sp(2))

    bom_data = [
        ["Componente", "Cantidad", "Función", "Costo USD (est.)"],
        ["Arduino Uno R3 (ATmega328P)", "1", "Controlador principal", "$5–9"],
        ["ESP32 DevKit v1", "1", "Servidor web WiFi", "$6–9"],
        ["Sensor ultrasónico HC-SR04", "1", "Medición de nivel", "$2–4"],
        ["Caudalímetro GFS401 (YF-S201)", "1", "Medición de caudal", "$3–5"],
        ["Bomba DC sumergible 5V/12V", "2", "Llenado y drenaje", "$3–6 c/u"],
        ["Módulo relé 2 canales (5V)", "1", "Actuación sobre bombas", "$1–2"],
        ["Resistencia 10 kΩ", "1", "Divisor de tensión (nivel)", "$0.05"],
        ["Resistencia 20 kΩ", "1", "Divisor de tensión (nivel)", "$0.05"],
        ["Cables Dupont M-M y M-H", "varios", "Interconexiones", "$2–4"],
        ["Protoboard 830 puntos", "1", "Montaje sin soldadura", "$2–4"],
        ["Fuente 5V/2A (USB o DC)", "1–2", "Alimentación microcontroladores", "$3–6"],
        ["Fuente 12V/1A (opcional)", "1", "Bombas de mayor potencia", "$3–6"],
        ["Manguera flexible (Ø8mm)", "1 m", "Interconexión hidráulica", "$1–2"],
        ["Abrazaderas/clips manguera", "4", "Fijación de conexiones", "$0.50"],
        ["Contenedor/depósito 5–20 L", "1", "Planta hidráulica", "$3–8"],
        ["TOTAL ESTIMADO", "—", "—", "$45–82 USD"],
    ]
    story.append(make_table(bom_data[0:1], bom_data[1:-1], styles,
                            col_widths=[6*cm, 2*cm, 5.5*cm, 3.5*cm]))
    # Fila total
    total_row = Table([bom_data[-1]], colWidths=[6*cm, 2*cm, 5.5*cm, 3.5*cm])
    total_row.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), AZUL_OSCURO),
        ('TEXTCOLOR', (0,0), (-1,-1), BLANCO),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(total_row)
    story.append(PageBreak())

    # ════════════════════════════════════════════════════════════
    # SECCIÓN 13 – TROUBLESHOOTING
    # ════════════════════════════════════════════════════════════
    story.append(section_header("GUÍA DE RESOLUCIÓN DE PROBLEMAS", "13", styles))
    story.append(sp(2))

    trouble_data = [
        ["Síntoma", "Causa Probable", "Solución"],
        ["App web no carga", "No conectado a WiFi del AP",
         "Verificar conexión a 'ESP32-Llenado', contraseña 'control2026'"],
        ["Nivel siempre 0% o 100%", "MAX_DIST_CM incorrecto",
         "Medir distancia vacío con cinta, actualizar config_arduino.h"],
        ["Caudal siempre 0 L/min", "GFS401 no en pin 2 o sin alimentación",
         "Verificar cableado pin 2 (INT0), comprobar 5V al sensor"],
        ["Bombas no responden", "Relé no conectado o lógica invertida",
         "Verificar IN1/IN2 al relé, relé es activo LOW (pin LOW=ON)"],
        ["ESP32 no arranca tras upload", "Error de compilación",
         "Revisar errores en Arduino IDE, verificar selección de placa ESP32"],
        ["Arduino se resetea al activar bomba", "Pico de corriente en arranque",
         "Usar fuente de alimentación separada para las bombas"],
        ["'Sin conexión' en la web", "Arduino no envía datos serial",
         "Verificar SoftwareSerial pines 10/11, divisor de tensión"],
        ["Nivel oscila mucho", "Ruido excesivo en HC-SR04",
         "Aumentar LECTURAS_PROMEDIO en config_arduino.h (hasta 5–10)"],
        ["Alarma permanente con bomba ON", "Caudal bajo por obstrucción",
         "Verificar que la tubería no esté doblada o bloqueada"],
        ["Setpoint no cambia desde web", "Comando POST /cmd no llega",
         "Verificar conexión WiFi activa y URL correcta 192.168.4.1"],
    ]
    story.append(make_table(trouble_data[0:1], trouble_data[1:], styles,
                            col_widths=[4*cm, 4.5*cm, 8.5*cm]))
    story.append(PageBreak())

    # ════════════════════════════════════════════════════════════
    # SECCIÓN 14 – SECUENCIA DE OPERACIÓN
    # ════════════════════════════════════════════════════════════
    story.append(section_header("SECUENCIA DE OPERACIÓN", "14", styles))
    story.append(sp(2))

    story.append(subsection_header("Arranque y Puesta en Marcha", styles))
    for i, step in enumerate([
        "Conectar fuente de alimentación al Arduino Uno (USB o DC 7–12V).",
        "Conectar ESP32 (puede usar el mismo USB del computador o fuente independiente).",
        "Esperar 5 segundos para que ambos microcontroladores inicialicen completamente.",
        "Desde el teléfono o computador, buscar la red WiFi <b>ESP32-Llenado</b>.",
        "Conectarse con la contraseña <b>control2026</b>.",
        "Abrir navegador web y acceder a <b>http://192.168.4.1</b>.",
        "Verificar que el estado muestre <b>'Conectado'</b> con timestamp en verde.",
        "En modo <b>AUTO</b> (default): el sistema llena hasta el setpoint (80%) automáticamente.",
        "Ajustar el setpoint con el slider si se desea otro nivel objetivo.",
        "Para pruebas manuales: cambiar a modo <b>MANUAL</b> y controlar cada bomba individualmente.",
        "Para drenar: activar Bomba 2 en modo MANUAL.",
    ], 1):
        story.append(Paragraph(f"<b>{i}.</b>  {step}", styles['bullet']))

    story.append(sp(2))
    story.append(subsection_header("Diagrama de Estados del Sistema", styles))
    story.append(sp())
    story.append(Paragraph(
        "Estado IDLE → (power ON) → INICIALIZANDO → (5s) → OPERACIÓN AUTO\n"
        "OPERACIÓN AUTO:\n"
        "  [nivel < SP-H]  →  Bomba1 ON  (llenando)\n"
        "  [nivel ∈ [SP-H, SP+H]]  →  Sin cambio (banda muerta)\n"
        "  [nivel > SP+H]  →  Bomba1 OFF  (deteniendo)\n"
        "OPERACIÓN AUTO → (comando M:0) → OPERACIÓN MANUAL\n"
        "OPERACIÓN MANUAL → (comando M:1) → OPERACIÓN AUTO\n"
        "CUALQUIER ESTADO → (Bomba1 ON y Q < 0.5) → ALARMA (estado paralelo)",
        styles['code']))
    story.append(PageBreak())

    # ════════════════════════════════════════════════════════════
    # SECCIÓN 15 – MEJORAS FUTURAS
    # ════════════════════════════════════════════════════════════
    story.append(section_header("MEJORAS FUTURAS Y LÍNEAS DE DESARROLLO", "15", styles))
    story.append(sp(2))

    mejoras = [
        ["Prioridad", "Mejora", "Beneficio Esperado"],
        ["Alta", "Implementar controlador PID",
         "Respuesta más rápida, menor oscilación que histéresis"],
        ["Alta", "Desplegar controlador LQR diseñado en MATLAB",
         "Control óptimo con mínimo esfuerzo de control"],
        ["Alta", "Control PWM de bombas (velocidad variable)",
         "Elimina ON/OFF, control continuo del caudal"],
        ["Media", "Filtro de Kalman para fusión de sensores",
         "Estimación de estado más robusta ante ruido"],
        ["Media", "Registro de datos en tarjeta SD",
         "Trazabilidad temporal, análisis offline"],
        ["Media", "Comunicación MQTT a broker cloud",
         "Monitoreo remoto desde cualquier ubicación"],
        ["Media", "Sensor de presión adicional",
         "Segunda variable controlada, sistema MIMO"],
        ["Baja", "Integración con SCADA (Modbus/OPC-UA)",
         "Compatibilidad con sistemas industriales"],
        ["Baja", "App móvil nativa (Flutter/React Native)",
         "Mejor experiencia de usuario que web embebida"],
        ["Investigación", "Control predictivo MPC",
         "Óptimo con restricciones explícitas de nivel/caudal"],
    ]
    story.append(make_table(mejoras[0:1], mejoras[1:], styles,
                            col_widths=[2*cm, 6.5*cm, 8.5*cm]))
    story.append(PageBreak())

    # ════════════════════════════════════════════════════════════
    # SECCIÓN 16 – REFERENCIAS
    # ════════════════════════════════════════════════════════════
    story.append(section_header("REFERENCIAS BIBLIOGRÁFICAS", "16", styles))
    story.append(sp(2))

    refs = [
        "[1] Ogata, K. (2010). <i>Modern Control Engineering</i>, 5ª edición. Prentice Hall.",
        "[2] Nise, N. S. (2019). <i>Control Systems Engineering</i>, 8ª edición. Wiley.",
        "[3] Franklin, G. F., Powell, J. D., & Emami-Naeini, A. (2015). "
            "<i>Feedback Control of Dynamic Systems</i>, 7ª edición. Pearson.",
        "[4] Åström, K. J., & Wittenmark, B. (1997). "
            "<i>Computer-Controlled Systems: Theory and Design</i>. Prentice Hall.",
        "[5] Espressif Systems. (2023). <i>ESP32 Technical Reference Manual v5.x</i>. espressif.com.",
        "[6] Microchip Technology. (2022). <i>ATmega328P Datasheet</i>. microchip.com.",
        "[7] Arduino. (2024). <i>Arduino Reference – SoftwareSerial Library</i>. arduino.cc.",
        "[8] ARDUINO. (2024). <i>HC-SR04 Ultrasonic Sensor Datasheet</i>.",
        "[9] Seeed Studio. (2023). <i>YF-S201 Water Flow Sensor Manual</i>.",
        "[10] MATLAB. (2023). <i>Control System Toolbox – lqr() Reference</i>. MathWorks.",
        "[11] Hunter, J. D. (2007). Matplotlib: A 2D Graphics Environment. "
             "<i>Computing in Science & Engineering</i>, 9(3), 90–95.",
    ]
    for ref in refs:
        story.append(Paragraph(ref, styles['body']))
        story.append(sp(0.5))

    story.append(sp(2))
    story.append(HRFlowable(width=17*cm, thickness=1, color=AZUL_CLARO))
    story.append(sp(2))

    # Página de cierre
    cierre_data = [
        [Paragraph("FIN DEL DOCUMENTO", ParagraphStyle(
            'fin', parent=styles['portada_titulo'],
            fontSize=18, textColor=BLANCO))],
        [Spacer(1, 0.5*cm)],
        [Paragraph(
            "Sistema de Llenado de Flujo Continuo con Control Automático<br/>"
            "Universidad Santiago Mariño – Teoría Moderna de Control",
            ParagraphStyle('finbody', parent=styles['portada_info'],
                           fontSize=11))],
        [Spacer(1, 0.5*cm)],
        [Paragraph(
            "<b>Autor:</b>  Neil Edickson Suarez Arevalo  (NeilsAraquitec)<br/>"
            "<b>Co-Autor:</b>  Jose Fabien Salas Garcia",
            ParagraphStyle('finauthor', parent=styles['portada_info'],
                           fontSize=11, textColor=HexColor("#B3E5FC")))],
        [Spacer(1, 0.3*cm)],
        [Paragraph(f"Generado el {datetime.datetime.now().strftime('%d de %B de %Y, %H:%M')}",
                   ParagraphStyle('findate', parent=styles['portada_info'],
                                  fontSize=9, textColor=HexColor("#90CAF9")))],
    ]
    cierre_table = Table(cierre_data, colWidths=[w])
    cierre_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), AZUL_OSCURO),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 20),
        ('RIGHTPADDING', (0,0), (-1,-1), 20),
    ]))
    story.append(cierre_table)

    # ────────────────────────────────────────────────────────────
    # BUILD
    # ────────────────────────────────────────────────────────────
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"\n[OK]  PDF generado exitosamente:\n   {output_path}\n")


# ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output = os.path.join(base_dir,
        "Resumen_Hiper_Detallado_Sistema_Llenado_NeilSuarez_JoseSalas.pdf")
    build_pdf(output)
