# Calculadora de Estación de Bombeo

Aplicación web para calcular parámetros de estaciones de bombeo usando la ecuación de Darcy-Weisbach. Esta aplicación está contenerizada para facilitar su despliegue en cualquier plataforma.

## Características Principales
- **Cálculos hidráulicos completos**:
  - Altura dinámica total (Total Dynamic Head)
  - Pérdidas por fricción
  - Potencia requerida (kW y HP)
- **Materiales de tubería soportados**: PVC, acero, cobre, concreto, hierro dúctil
- **Interfaz moderna y responsiva** con Bootstrap 5
- **Visualización gráfica** de la curva de la bomba y punto de operación
- **Unidades abreviadas** (m, ft, km, in, mm) para mejor experiencia de usuario
- **Animaciones y notificaciones** para resultados y errores
- **Despliegue sencillo** con Docker

## Tecnologías Utilizadas
- **Frontend**: HTML5, CSS3, JavaScript (Chart.js para gráficos), Bootstrap 5
- **Backend**: Python 3.9+, FastAPI
- **Contenedorización**: Docker, Docker Compose
- **Dependencias principales**: 
  - Backend: numpy, fastapi, uvicorn, pydantic, reportlab, jinja2, matplotlib
  - Frontend: Bootstrap 5, Chart.js

## Instalación y Uso

### Requisitos Previos
- Docker y Docker Compose instalados
- Git (opcional, solo para clonar el repositorio)

### Opción 1: Usando Docker (Recomendado)

1. Clonar el repositorio (o descargar el código fuente):
   ```bash
   git clone https://github.com/tu-usuario/pumping-station-calculator.git
   cd pumping-station-calculator
   ```

2. Construir y ejecutar con Docker Compose:
   ```bash
   docker-compose up --build
   ```
   La aplicación estará disponible en: http://localhost:8001

3. Para detener la aplicación:
   ```bash
   docker-compose down
   ```

### Opción 2: Instalación Manual

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/tu-usuario/pumping-station-calculator.git
   cd pumping-station-calculator
   ```

2. Crear y activar un entorno virtual (recomendado):
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: .\venv\Scripts\activate
   ```

3. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

4. Iniciar el servidor:
   ```bash
   uvicorn main:app --reload
   ```
   La aplicación estará disponible en: http://localhost:8000

## Estructura del Proyecto
```
pumping-station/
├── Dockerfile           # Configuración de Docker
├── docker-compose.yml   # Configuración de Docker Compose
├── requirements.txt     # Dependencias de Python
├── main.py             # Aplicación principal FastAPI
├── frontend/           # Archivos del frontend
│   ├── static/         # Archivos estáticos (CSS, JS, imágenes)
│   └── templates/      # Plantillas HTML
└── README.md           # Este archivo
```

## Solución de Problemas

### Puerto en Uso
Si el puerto 8001 ya está en uso, puedes cambiarlo modificando el archivo `docker-compose.yml`:
```yaml
ports:
  - "8002:8000"  # Cambia el primer número al puerto deseado
```

### Problemas con Docker
Si experimentas problemas con Docker, intenta:
1. Limpiar la caché de Docker:
   ```bash
   docker system prune -a
   ```
2. Verificar que el servicio de Docker esté en ejecución
3. Asegurarte de tener los permisos necesarios (en Linux, agregar tu usuario al grupo docker)

## Licencia
MIT License - [Ver archivo LICENSE](LICENSE)

## Contribución
Las contribuciones son bienvenidas. Por favor, lee las [pautas de contribución](CONTRIBUTING.md) antes de enviar cambios.
