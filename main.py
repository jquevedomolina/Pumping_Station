from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import math
from datetime import datetime
from fastapi.responses import Response
import matplotlib.pyplot as plt
import matplotlib
import numpy as np

# Configure matplotlib for headless operation
matplotlib.use('Agg')
import base64
import io

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurar archivos estáticos y templates
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
app.mount("/image", StaticFiles(directory="frontend/image"), name="image")

templates = Jinja2Templates(directory="frontend/templates")

# Configurar el favicon
from fastapi.responses import FileResponse
from pathlib import Path

@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    favicon_path = Path("frontend/image/favicon.png")
    if not favicon_path.exists():
        favicon_path = Path("frontend/static/favicon.ico")
    return FileResponse(favicon_path)

from typing import Optional

class PumpingStationInput(BaseModel):
    project_name: Optional[str] = ""
    project_location: Optional[str] = ""
    geometric_height: float
    geometric_height_unit: str
    flow_rate: float
    flow_rate_unit: str
    pipe_length: float
    pipe_length_unit: str
    pipe_diameter: float
    pipe_diameter_unit: str
    pipe_material: str
    pump_efficiency: float

    # Accesorios (opcionales, por defecto 0)
    valve_gate: Optional[int] = 0
    valve_butterfly: Optional[int] = 0
    valve_check: Optional[int] = 0
    valve_globe: Optional[int] = 0 # Usaremos 'globe' para reguladoras/sostenedoras
    elbow_90: Optional[int] = 0
    elbow_45: Optional[int] = 0

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get('/root')
async def root():
    return {'message': 'hello pumping station'}

def calculate_pumping_station(data: PumpingStationInput):
    """
    Calculate pumping station parameters using Darcy-Weisbach equation
    """
    print(f"\n=== Nuevo cálculo ===")
    print(f"Datos de entrada: {data.dict()}")
    
    # Convert units
    flow_rate_m3s = data.flow_rate / 1000  # l/s to m3/s
    diameter_m = data.pipe_diameter / 1000  # mm to m
    
    # Get roughness coefficient based on material
    roughness = {
        "pvc": 0.00015,
        "steel": 0.000045,
        "copper": 0.0000015,
        "concrete": 0.0003,
        "ductile_iron": 0.00015  # Hierro dúctil
    }.get(data.pipe_material.lower(), 0.0015)  # mm
    print(f"Coeficiente de rugosidad: {roughness} mm")
    
    # Calculate Reynolds number
    kinematic_viscosity = 1.004e-6  # m2/s for water at 20°C
    # --- Conversión de Unidades a SI ---
    # Altura Geométrica (a metros)
    geometric_height_m = data.geometric_height
    if data.geometric_height_unit == 'ft':
        geometric_height_m *= 0.3048

    # Caudal (a m³/s)
    flow_rate_m3s = data.flow_rate
    if data.flow_rate_unit == 'l/s':
        flow_rate_m3s /= 1000
    elif data.flow_rate_unit == 'm3/h':
        flow_rate_m3s /= 3600
    elif data.flow_rate_unit == 'gpm':
        flow_rate_m3s *= 6.309e-5

    # Longitud de Tubería (a metros)
    pipe_length_m = data.pipe_length
    if data.pipe_length_unit == 'km':
        pipe_length_m *= 1000
    elif data.pipe_length_unit == 'ft':
        pipe_length_m *= 0.3048
    elif data.pipe_length_unit == 'mi':
        pipe_length_m *= 1609.34

    # Diámetro de Tubería (a metros)
    diameter_m = data.pipe_diameter
    if data.pipe_diameter_unit == 'mm':
        diameter_m /= 1000
    elif data.pipe_diameter_unit == 'in':
        diameter_m *= 0.0254

    velocity = flow_rate_m3s / (math.pi * (diameter_m**2)/4)
    reynolds = velocity * diameter_m / kinematic_viscosity
    
    # Calculate friction factor (Darcy-Weisbach)
    if reynolds < 2000:
        friction_factor = 64 / reynolds
    else:
        # Colebrook-White approximation
        friction_factor = 0.25 / (math.log10((roughness/1000)/(3.7*diameter_m) + 5.74/(reynolds**0.9)))**2
    
    # Calculate head loss por fricción
    gravity = 9.80665  # m/s2 (standard gravity)
    head_loss_friction = friction_factor * (pipe_length_m/diameter_m) * (velocity**2)/(2*gravity)

    # --- Cálculo de Pérdidas Menores por Accesorios ---
    k_values = {
        'valve_gate': 0.2,       # Válvula de compuerta
        'valve_butterfly': 0.3,  # Válvula mariposa
        'valve_check': 2.0,      # Válvula check (tipo clapeta)
        'valve_globe': 10.0,     # Válvula de globo (para regulación)
        'elbow_90': 0.9,         # Codo de 90 grados
        'elbow_45': 0.4          # Codo de 45 grados
    }
    total_k = (
        data.valve_gate * k_values['valve_gate'] +
        data.valve_butterfly * k_values['valve_butterfly'] +
        data.valve_check * k_values['valve_check'] +
        data.valve_globe * k_values['valve_globe'] +
        data.elbow_90 * k_values['elbow_90'] +
        data.elbow_45 * k_values['elbow_45']
    )
    head_loss_minor = total_k * (velocity**2) / (2 * gravity)
    
    # Total dynamic head
    total_head = geometric_height_m + head_loss_friction + head_loss_minor
    
    # Power calculation with precise constants
    water_density = 1000  # kg/m3
    gravity = 9.80665  # m/s2 (standard gravity)
    if flow_rate_m3s <= 0 or total_head <= 0:
        print("¡Advertencia! Valores de entrada inválidos para cálculo de potencia")
    power_watts = (water_density * gravity * flow_rate_m3s * total_head) / data.pump_efficiency
    power_kw = power_watts / 1000
    power_hp = power_kw * 1.34102  # Conversión de kW a HP (1 kW = 1.34102 HP)
    print(f"Power calc: {power_watts:.2f} W = {power_kw:.4f} kW = {power_hp:.4f} HP (ρ={water_density} kg/m3, g={gravity} m/s2, η={data.pump_efficiency})")
    
    # --- Generación de Curva de Bomba de 3 Puntos ---
    # 1. Definir los 3 puntos clave de la curva de la bomba
    # Punto de operación (BEP - Best Efficiency Point)
    bep_head = total_head
    bep_flow_m3s = flow_rate_m3s
    
    # Punto de Cierre (Shutoff Head, Q=0)
    shutoff_head = bep_head * 1.33  # Estimación común: 133% de la altura en BEP
    
    # Punto de Máximo Caudal (Runout, H=0)
    max_flow_m3s = bep_flow_m3s * 2.0  # Estimación común: 200% del caudal en BEP

    # 2. Calcular coeficientes de la parábola H = A - B*Q^2
    # En Q=0, H = A, por lo tanto A es el shutoff_head
    A = shutoff_head
    # Usamos el punto de máximo caudal para encontrar B
    if max_flow_m3s > 0:
        B = A / (max_flow_m3s**2)
    else:
        B = 0

    # 3. Generar los puntos de la curva para la gráfica
    curve_points = []
    steps = 20  # Generar 21 puntos para una curva suave
    for i in range(steps + 1):
        q_m3s = (i / steps) * max_flow_m3s
        h = A - B * (q_m3s**2)
        curve_points.append({
            "flow": round(q_m3s, 4),
            "head": round(h, 2),
            "flow_ls": round(q_m3s * 1000, 1)
        })
    
    # Resultados
    return {
        "total_head": round(total_head, 2),
        "geometric_height": round(geometric_height_m, 2),
        "friction_head_loss": round(head_loss_friction, 2),
        "minor_head_loss": round(head_loss_minor, 2),
        "power_kw": round(power_kw, 4) if power_kw < 1 else round(power_kw, 2),  # Más decimales para valores pequeños
        "power_hp": round(power_hp, 4) if power_hp < 1 else round(power_hp, 2),  # Potencia en HP
        "velocity": round(velocity, 2),
        "reynolds": round(reynolds, 2),
        "friction_factor": round(friction_factor, 6),
        "flow_rate": round(flow_rate_m3s * 1000, 1),  # Caudal en l/s para el punto de operación
        "flow_rate_m3s": round(flow_rate_m3s, 6),  # Caudal en m3/s para cálculos
        "pump_curve": curve_points,
        "bep_flow_ls": round(bep_flow_m3s * 1000, 1),
        # La ecuación debe usar Q en l/s, por lo que el coeficiente B debe ser ajustado (dividido por 1000^2)
        "curve_equation": f"H = {round(A, 2)} - {B / (1000**2):.4f}·Q²"
    }
    
    print("Resultados:")
    for key, value in results.items():
        print(f"{key}: {value}")
    
    return results

@app.post('/calculate')
async def calculate(data: PumpingStationInput):
    try:
        results = calculate_pumping_station(data)
        return results
    except Exception as e:
        print(f"Error en cálculo: {str(e)}")
        return {"error": str(e)}

def generate_pump_curve_chart(results):
    """Generate pump curve chart with multiple flow rate axes and return as base64 encoded image"""
    try:
        # Create figure with larger size to accommodate multiple axes
        fig, ax1 = plt.subplots(figsize=(12, 8))
        
        # Generate flow rate range (0 to 150% of design flow)
        flow_design = results.get('flow_rate_m3s', 0.05)  # Default if not available
        flow_range = np.linspace(0, flow_design * 1.5, 100)
        
        # Calculate head values using pump curve equation
        # H = a*Q^2 + b*Q + c (typical pump curve)
        total_head = results.get('total_head', 20)
        
        # Simple quadratic pump curve approximation
        # Assume pump can deliver 120% of required head at zero flow
        # and drops to 80% at 150% flow
        a = -0.4 * total_head / (flow_design * 1.5)**2
        b = 0
        c = 1.2 * total_head
        
        head_values = a * flow_range**2 + b * flow_range + c
        
        # Plot pump curve (using m³/s as base unit)
        ax1.plot(flow_range, head_values, 'b-', linewidth=3, label='Curva de Bomba', zorder=3)
        
        # Plot operating point
        ax1.plot(flow_design, total_head, 'ro', markersize=10, label='Punto de Operación', zorder=4)
        
        # Add system curve (simplified)
        system_head = results.get('geometric_height', 17) + (flow_range / flow_design)**2 * results.get('friction_head_loss', 3)
        ax1.plot(flow_range, system_head, 'g--', linewidth=2.5, label='Curva del Sistema', zorder=2)
        
        # PRIMARY AXIS (m³/s) - Bottom
        ax1.set_xlabel('Caudal (m³/s)', fontsize=12, fontweight='bold', color='#1B2951')
        ax1.set_ylabel('Altura (m)', fontsize=12, fontweight='bold', color='#1B2951')
        ax1.tick_params(axis='x', colors='#1B2951', labelsize=10)
        ax1.tick_params(axis='y', colors='#1B2951', labelsize=10)
        
        # SECONDARY AXIS (l/s) - Top
        ax2 = ax1.twiny()
        ax2.set_xlim(ax1.get_xlim())
        # Convert m³/s to l/s (multiply by 1000)
        ax2_ticks = ax1.get_xticks()
        ax2.set_xticks(ax2_ticks)
        ax2.set_xticklabels([f'{tick*1000:.1f}' for tick in ax2_ticks])
        ax2.set_xlabel('Caudal (l/s)', fontsize=12, fontweight='bold', color='#00BFFF')
        ax2.tick_params(axis='x', colors='#00BFFF', labelsize=10)
        
        # THIRD AXIS (GPM) - Top right
        ax3 = ax1.twiny()
        ax3.spines['top'].set_position(('outward', 40))
        ax3.set_xlim(ax1.get_xlim())
        # Convert m³/s to GPM (multiply by 15850.3)
        ax3_ticks = ax1.get_xticks()
        ax3.set_xticks(ax3_ticks)
        ax3.set_xticklabels([f'{tick*15850.3:.0f}' for tick in ax3_ticks])
        ax3.set_xlabel('Caudal (GPM)', fontsize=12, fontweight='bold', color='#FF6B35')
        ax3.tick_params(axis='x', colors='#FF6B35', labelsize=10)
        
        # Remove title - will be handled by PDF header
        
        # Grid and styling
        ax1.grid(True, alpha=0.4, linestyle='--', color='gray')
        ax1.set_facecolor('#FAFBFC')
        
        # Legend positioned in bottom right corner
        ax1.legend(loc='lower right', frameon=True, fancybox=True, shadow=True, 
                  fontsize=11, bbox_to_anchor=(0.98, 0.02))
        
        # Enhanced annotations with multiple units
        flow_ls = flow_design * 1000  # l/s
        flow_gpm = flow_design * 15850.3  # GPM
        
        annotation_text = f'Punto de Operación\n' \
                         f'Q = {flow_design:.4f} m³/s\n' \
                         f'Q = {flow_ls:.1f} l/s\n' \
                         f'Q = {flow_gpm:.0f} GPM\n' \
                         f'H = {total_head:.1f} m'
        
        ax1.annotate(annotation_text,
                    xy=(flow_design, total_head),
                    xytext=(flow_design * 0.15, total_head * 0.7),
                    arrowprops=dict(arrowstyle='->', color='red', lw=2),
                    fontsize=9, ha='left', va='center',
                    bbox=dict(boxstyle='round,pad=0.4', facecolor='yellow', 
                             edgecolor='red', alpha=0.9, linewidth=1.5))
        
        # Set limits with some padding
        ax1.set_xlim(0, flow_design * 1.6)
        ax1.set_ylim(0, max(head_values) * 1.2)
        
        # Save to base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close(fig)
        
        return f"data:image/png;base64,{image_base64}"
    except Exception as e:
        print(f"Error generating chart: {str(e)}")
        return None

@app.post('/generate-report')
async def generate_report(data: PumpingStationInput):
    try:
        # Calculate results
        results = calculate_pumping_station(data)
        
        # Get current date
        current_date = datetime.now().strftime("%d/%m/%Y")
        
        # Generate pump curve chart
        chart_image = generate_pump_curve_chart(results)
        
        # Render HTML template
        html_content = templates.get_template("report.html").render(
            request=Request,
            data=data.dict(),
            results=results,
            current_date=current_date,
            chart_image=chart_image
        )
        
        # Generate Professional PDF using ReportLab
        try:
            from reportlab.lib.pagesizes import legal
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, BaseDocTemplate, PageTemplate, Frame
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch, mm
            from reportlab.lib import colors
            from reportlab.platypus.flowables import HRFlowable
            from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
            import os
            
            buffer = io.BytesIO()
            
            # Create custom document with header and footer
            class HeaderFooterDocTemplate(BaseDocTemplate):
                def __init__(self, filename, **kwargs):
                    BaseDocTemplate.__init__(self, filename, **kwargs)
                    
                def build_header_footer(self, canvas, doc):
                    # Header
                    canvas.saveState()
                    
                    # Company name - left aligned with blue line
                    canvas.setFont('Helvetica-Bold', 20)
                    canvas.setFillColor(colors.HexColor('#1B2951'))
                    company_name = 'VMS HYDRAULICS, S.A.'
                    canvas.drawString(50, legal[1] - 50, company_name)
                    
                    # Tagline - left aligned below company name
                    canvas.setFont('Helvetica-Oblique', 12)
                    canvas.setFillColor(colors.HexColor('#666666'))
                    tagline = 'Válvulas, mediciones y soluciones hidráulicas'
                    canvas.drawString(50, legal[1] - 70, tagline)
                    
                    # Date and version info - right aligned
                    canvas.setFont('Helvetica', 10)
                    canvas.setFillColor(colors.HexColor('#666666'))
                    current_date = datetime.now().strftime("%d/%m/%Y")
                    canvas.drawRightString(legal[0] - 50, legal[1] - 50, current_date)
                    canvas.drawRightString(legal[0] - 50, legal[1] - 65, 'Sistema v2.0 Pro')
                    
                    # Header line - full width
                    canvas.setStrokeColor(colors.HexColor('#00BFFF'))
                    canvas.setLineWidth(3)
                    canvas.line(50, legal[1] - 85, legal[0] - 50, legal[1] - 85)
                    
                    # Footer
                    footer_y = 40
                    
                    # Footer line
                    canvas.setStrokeColor(colors.HexColor('#BDC3C7'))
                    canvas.setLineWidth(1)
                    canvas.line(50, footer_y + 25, legal[0] - 50, footer_y + 25)
                    
                    # Footer text
                    canvas.setFont('Helvetica-Bold', 8)
                    canvas.setFillColor(colors.HexColor('#7F8C8D'))
                    canvas.drawString(50, footer_y + 10, 'VMS HYDRAULICS, S.A. - Válvulas, mediciones y soluciones hidráulicas')
                    
                    canvas.setFont('Helvetica', 8)
                    canvas.drawString(50, footer_y - 2, f'Reporte generado el {datetime.now().strftime("%d/%m/%Y")} | Sistema de Cálculo Hidráulico v2.0 Pro')
                    canvas.drawString(50, footer_y - 14, 'Este reporte ha sido generado automáticamente y debe ser revisado por un ingeniero calificado.')
                    
                    canvas.setFont('Helvetica-Oblique', 8)
                    canvas.drawString(50, footer_y - 26, 'Certificado ISO 9001 - Calidad garantizada en soluciones hidráulicas')
                    
                    # Page number
                    canvas.setFont('Helvetica', 8)
                    canvas.drawRightString(legal[0] - 50, footer_y + 10, f'Página {doc.page}')
                    
                    canvas.restoreState()
            
            # Create document with custom template
            doc = HeaderFooterDocTemplate(
                buffer,
                pagesize=legal,
                rightMargin=50,
                leftMargin=50,
                topMargin=120,  # Increased to accommodate header
                bottomMargin=80  # Increased to accommodate footer
            )
            
            # Create frame for content
            frame = Frame(
                50, 80, legal[0] - 100, legal[1] - 200,
                leftPadding=0, bottomPadding=0, rightPadding=0, topPadding=0
            )
            
            # Create page template
            template = PageTemplate(id='normal', frames=frame, onPage=doc.build_header_footer)
            doc.addPageTemplates([template])
            
            # Custom styles
            styles = getSampleStyleSheet()
            
            # Company header style
            company_style = ParagraphStyle(
                'CompanyHeader',
                parent=styles['Normal'],
                fontSize=24,
                textColor=colors.HexColor('#00BFFF'),
                fontName='Helvetica-Bold',
                alignment=TA_CENTER,
                spaceAfter=5
            )
            
            tagline_style = ParagraphStyle(
                'Tagline',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.HexColor('#666666'),
                fontName='Helvetica-Oblique',
                alignment=TA_CENTER,
                spaceAfter=20
            )
            
            title_style = ParagraphStyle(
                'ReportTitle',
                parent=styles['Heading1'],
                fontSize=20,
                textColor=colors.HexColor('#2C3E50'),
                fontName='Helvetica-Bold',
                alignment=TA_CENTER,
                spaceAfter=30,
                spaceBefore=20
            )
            
            section_style = ParagraphStyle(
                'SectionHeader',
                parent=styles['Heading2'],
                fontSize=16,
                textColor=colors.HexColor('#00BFFF'),
                fontName='Helvetica-Bold',
                spaceBefore=20,
                spaceAfter=15,
                borderWidth=0,
                borderColor=colors.HexColor('#00BFFF'),
                borderPadding=5
            )
            
            subsection_style = ParagraphStyle(
                'SubsectionHeader',
                parent=styles['Heading3'],
                fontSize=12,
                textColor=colors.HexColor('#34495E'),
                fontName='Helvetica-Bold',
                spaceBefore=15,
                spaceAfter=10
            )
            
            normal_style = ParagraphStyle(
                'CustomNormal',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.HexColor('#2C3E50'),
                fontName='Helvetica',
                alignment=TA_JUSTIFY,
                spaceAfter=8
            )
            
            # Build PDF content
            story = []
            
            # Enhanced report title
            story.append(Paragraph("REPORTE TÉCNICO DE ESTACIÓN DE BOMBEO", title_style))
            
            # Project information box
            project_data = [
                ['INFORMACIÓN DEL PROYECTO', '', ''],
                ['Proyecto:', data.dict().get('project_name', 'N/A'), ''],
                ['Ubicación:', data.dict().get('project_location', 'N/A'), ''],
                ['Fecha de reporte:', current_date, ''],
                ['Elaborado por:', 'VMS HYDRAULICS', '']
            ]
            
            project_table = Table(project_data, colWidths=[2.5*inch, 3*inch, 1*inch])
            project_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#00BFFF')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('SPAN', (0, 0), (-1, 0)),
                ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F8F9FA')),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#BDC3C7')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8)
            ]))
            
            story.append(project_table)
            story.append(Spacer(1, 30))
            
            # Input parameters section
            story.append(Paragraph("1. PARÁMETROS DE ENTRADA", section_style))
            
            input_data = [
                ['PARÁMETRO', 'VALOR', 'UNIDAD', 'DESCRIPCIÓN'],
                ['Altura Geométrica', f"{data.geometric_height:.2f}", data.geometric_height_unit, 'Diferencia de elevación'],
                ['Caudal de Diseño', f"{data.flow_rate:.2f}", data.flow_rate_unit, 'Flujo volumetrico requerido'],
                ['Longitud de Tubería', f"{data.pipe_length:.2f}", data.pipe_length_unit, 'Longitud total del sistema'],
                ['Diámetro de Tubería', f"{data.pipe_diameter:.2f}", data.pipe_diameter_unit, 'Diámetro interno de tubería'],
                ['Material de Tubería', data.pipe_material.replace('_', ' ').title(), '', 'Material de construcción'],
                ['Eficiencia de Bomba', f"{data.pump_efficiency * 100:.1f}", '%', 'Eficiencia mecánica de la bomba']
            ]
            
            # Add accessories if any
            accessories = []
            if data.valve_gate > 0: accessories.append(f"Válvulas compuerta: {data.valve_gate}")
            if data.valve_butterfly > 0: accessories.append(f"Válvulas mariposa: {data.valve_butterfly}")
            if data.valve_check > 0: accessories.append(f"Válvulas check: {data.valve_check}")
            if data.valve_globe > 0: accessories.append(f"Válvulas globo: {data.valve_globe}")
            if data.elbow_90 > 0: accessories.append(f"Codos 90°: {data.elbow_90}")
            if data.elbow_45 > 0: accessories.append(f"Codos 45°: {data.elbow_45}")
            
            if accessories:
                # Format accessories with line breaks for better readability
                accessories_text = '\n'.join(accessories)
                input_data.append(['Accesorios', accessories_text, '', 'Elementos adicionales del sistema'])
            
            input_table = Table(input_data, colWidths=[1.5*inch, 1.8*inch, 0.8*inch, 2.4*inch])
            input_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495E')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8F9FA')]),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#BDC3C7')),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6)
            ]))
            
            story.append(input_table)
            story.append(Spacer(1, 30))
            
            # Results section
            story.append(Paragraph("2. RESULTADOS DEL CÁLCULO HIDRÁULICO", section_style))
            
            # Key results in highlighted boxes
            key_results = [
                ['PARÁMETRO', 'VALOR', 'UNIDAD', 'OBSERVACIONES'],
                ['Altura Total Dinámica (TDH)', f"{results.get('total_head', 0):.2f}", 'm', 'Altura total que debe vencer la bomba'],
                ['Pérdidas por Fricción', f"{results.get('friction_head_loss', 0):.2f}", 'm', 'Pérdidas en tubería recta'],
                ['Pérdidas Menores', f"{results.get('minor_head_loss', 0):.2f}", 'm', 'Pérdidas en accesorios'],
                ['Velocidad del Flujo', f"{results.get('velocity', 0):.2f}", 'm/s', 'Velocidad promedio en tubería'],
                ['Número de Reynolds', f"{results.get('reynolds', 0):.0f}", '-', 'Caracterización del flujo'],
                ['Factor de Fricción', f"{results.get('friction_factor', 0):.6f}", '-', 'Coeficiente de Darcy-Weisbach']
            ]
            
            results_table = Table(key_results, colWidths=[1.8*inch, 1.2*inch, 0.8*inch, 2.7*inch])
            results_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E74C3C')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#FADBD8')]),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#BDC3C7')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6)
            ]))
            
            story.append(results_table)
            story.append(Spacer(1, 20))
            
            # Insert page break to move next section to page 2
            from reportlab.platypus import PageBreak
            story.append(PageBreak())
            
            # Power requirements - highlighted section (now on page 2)
            story.append(Paragraph("2.1 Requerimientos de Potencia", subsection_style))
            
            power_data = [
                ['TIPO DE POTENCIA', 'VALOR', 'UNIDAD'],
                ['Potencia Hidráulica', f"{results.get('power_kw', 0):.2f}", 'kW'],
                ['Potencia Hidráulica', f"{results.get('power_hp', 0):.2f}", 'HP'],
                ['Eficiencia Considerada', f"{data.pump_efficiency * 100:.1f}", '%']
            ]
            
            power_table = Table(power_data, colWidths=[2.5*inch, 1.5*inch, 1*inch])
            power_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27AE60')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#D5F4E6')),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#BDC3C7')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8)
            ]))
            
            story.append(power_table)
            story.append(Spacer(1, 30))
            
            # Add pump curve chart if available
            if chart_image:
                story.append(Paragraph("3. CURVA CARACTERÍSTICA DE LA BOMBA", section_style))
                
                # Chart subtitle with technical information
                chart_subtitle = Paragraph(
                    "Gráfico de rendimiento con ejes múltiples (m³/s, l/s, GPM) - Punto de operación y curvas del sistema",
                    ParagraphStyle(
                        'ChartSubtitle',
                        parent=normal_style,
                        fontSize=9,
                        textColor=colors.HexColor('#666666'),
                        fontName='Helvetica-Oblique',
                        alignment=TA_CENTER,
                        spaceAfter=15
                    )
                )
                story.append(chart_subtitle)
                # Convert base64 to image for ReportLab
                import base64
                from reportlab.lib.utils import ImageReader
                
                try:
                    # Remove data:image/png;base64, prefix
                    image_data = chart_image.split(',')[1]
                    image_bytes = base64.b64decode(image_data)
                    image_buffer = io.BytesIO(image_bytes)
                    
                    # Add image to PDF
                    img = Image(image_buffer, width=6*inch, height=3.6*inch)
                    story.append(img)
                    story.append(Spacer(1, 20))
                    
                    # Chart description
                    chart_desc = Paragraph(
                        "La gráfica muestra la curva característica de la bomba (línea azul), "
                        "el punto de operación del sistema (punto rojo) y la curva del sistema hidráulico (línea verde). "
                        "El punto de intersección indica las condiciones de operación óptimas.",
                        normal_style
                    )
                    story.append(chart_desc)
                    story.append(Spacer(1, 20))
                except Exception as e:
                    print(f"Error adding chart to PDF: {e}")
            
            # Technical notes
            story.append(Paragraph("4. NOTAS TÉCNICAS Y RECOMENDACIONES", section_style))
            
            notes_text = f"""
            <b>Método de Cálculo:</b> Los cálculos se basan en la ecuación de Darcy-Weisbach para pérdidas por fricción 
            y el método de coeficientes K para pérdidas menores.<br/><br/>
            
            <b>Consideraciones de Diseño:</b><br/>
            • La velocidad de flujo calculada es {results.get('velocity', 0):.2f} m/s<br/>
            • Se recomienda mantener velocidades entre 1.0 y 3.0 m/s para sistemas de bombeo<br/>
            • El número de Reynolds indica flujo {'turbulento' if results.get('reynolds', 0) > 4000 else 'laminar'}<br/><br/>
            
            <b>Recomendaciones:</b><br/>
            • Verificar que la bomba seleccionada opere en su rango de eficiencia óptima<br/>
            • Considerar un factor de seguridad del 10-15% en la potencia calculada<br/>
            • Instalar válvulas de control y medición según especificaciones del proyecto<br/>
            • Realizar mantenimiento preventivo según recomendaciones del fabricante
            """
            
            story.append(Paragraph(notes_text, normal_style))
            story.append(Spacer(1, 30))
            

            
            # Build PDF
            doc.build(story)
            pdf_content = buffer.getvalue()
            buffer.close()
            
        except ImportError:
            return {"error": "ReportLab no está instalado. Instale con: pip install reportlab"}
        except Exception as pdf_error:
            print(f"Error específico de ReportLab: {str(pdf_error)}")
            return {"error": f"Error generando PDF: {str(pdf_error)}"}
        
        return Response(
            content=pdf_content,
            media_type='application/pdf',
            headers={'Content-Disposition': 'attachment; filename="reporte_bombeo.pdf"'}
        )
    except Exception as e:
        print(f"Error en generación de reporte: {str(e)}")
        return {"error": f"Error generando reporte: {str(e)}"}
