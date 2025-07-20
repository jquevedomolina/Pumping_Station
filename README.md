# Calculadora de Estación de Bombeo

Aplicación web para calcular parámetros de estaciones de bombeo usando la ecuación de Darcy-Weisbach.

## Características Principales
- **Cálculos hidráulicos completos**:
  - Altura dinámica total (Total Dynamic Head)
  - Pérdidas por fricción
  - Potencia requerida (kW y HP)
- **Materiales de tubería soportados**: PVC, acero, cobre, concreto
- **Interfaz moderna y responsiva** con Bootstrap 5
- **Visualización gráfica** de la curva de la bomba y punto de operación
- **Unidades abreviadas** (m, ft, km, in, mm) para mejor experiencia de usuario
- **Animaciones y notificaciones** para resultados y errores

## Tecnologías Utilizadas
- **Frontend**: HTML5, CSS3 (diseño moderno con variables CSS), JavaScript (Chart.js para gráficos)
- **Backend**: Python 3.10+, FastAPI
- **Dependencias**: 
  - Backend: numpy, fastapi, uvicorn
  - Frontend: Bootstrap 5, Chart.js

## Instalación y Uso
1. Clonar repositorio:
   ```bash
   git clone https://github.com/tu-usuario/pumping-station-calculator.git
   cd pumping_station
   ```

2. Instalar dependencias del backend:
   ```bash
   pip install -r backend/requirements.txt
   ```

3. Iniciar backend:
   ```bash
   uvicorn backend.main:app --reload
   ```

4. Abrir `frontend/templates/index.html` en navegador

## Capturas de Pantalla
(Actualizar con imágenes tras implementación)

## Licencia
MIT License - [Detalles de licencia aquí]
