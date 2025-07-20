from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import math

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
app.mount("/static", StaticFiles(directory="../frontend/static"), name="static")
templates = Jinja2Templates(directory="../frontend/templates")

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
        "friction_head_loss": round(head_loss_friction, 2),
        "minor_head_loss": round(head_loss_minor, 2),
        "power_kw": round(power_kw, 4) if power_kw < 1 else round(power_kw, 2),  # Más decimales para valores pequeños
        "power_hp": round(power_hp, 4) if power_hp < 1 else round(power_hp, 2),  # Potencia en HP
        "velocity": round(velocity, 2),
        "reynolds": round(reynolds, 2),
        "friction_factor": round(friction_factor, 6),
        "flow_rate": round(flow_rate_m3s * 1000, 1),  # Caudal en l/s para el punto de operación
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
