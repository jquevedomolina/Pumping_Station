<div align="center">
  <img src="frontend/static/images/vms_logo.svg" alt="Logo" width="200">
  <h1>Calculadora de Estación de Bombeo</h1>
  <p>
    Solución integral para el cálculo de parámetros hidráulicos de estaciones de bombeo utilizando la ecuación de Darcy-Weisbach.
    <br />
    <a href="#características"><strong>Explorar características »</strong></a>
    <br />
    <br />
    <a href="#instalación">Ver instalación</a>
    ·
    <a href="#ejemplos">Ver ejemplos</a>
    ·
    <a href="#contribuir">Cómo contribuir</a>
  </p>
</div>

## 🌟 Características

La Calculadora de Estación de Bombeo ofrece una solución completa para ingenieros y técnicos que necesitan realizar cálculos hidráulicos precisos:

<div align="center">
  <img src="https://via.placeholder.com/800x400.png?text=Interfaz+de+Usuario" alt="Interfaz de Usuario" style="border-radius: 8px; margin: 20px 0;">
</div>

### 🔍 Cálculos Avanzados
- **Análisis hidráulico completo** usando la ecuación de Darcy-Weisbach
- **Cálculo de pérdidas de carga** en tuberías y accesorios
- **Selección de bombas** basada en curvas características
- **Análisis de NPSH** para prevenir cavitación

### 📊 Visualización de Datos
- Gráficos interactivos de curvas de bombas
- Diagramas de pérdidas de carga
- Exportación de informes en PDF

### 🛠️ Características Técnicas
- Interfaz web responsiva que funciona en cualquier dispositivo
- Cálculos en tiempo real
- Guardado de proyectos
- Compatibilidad con múltiples sistemas de unidades

## 🚀 Instalación Rápida

### Requisitos Previos
- Docker y Docker Compose instalados
- 2GB de RAM disponibles
- 1GB de espacio en disco

### Pasos de Instalación

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/tu-usuario/pumping-station-calculator.git
   cd pumping-station-calculator
   ```

2. **Iniciar con Docker Compose**
   ```bash
   docker-compose up -d --build
   ```

3. **Acceder a la aplicación**
   Abre tu navegador y visita:
   ```
   http://localhost:8001
   ```

<div align="center">
  <img src="https://via.placeholder.com/800x200.png?text=Diagrama+de+Arquitectura" alt="Arquitectura" style="border-radius: 8px; margin: 20px 0;">
</div>

## 🏗️ Estructura del Proyecto

```
pumping-station/
├── .github/            # Configuraciones de GitHub
│   └── workflows/      # CI/CD workflows
├── frontend/           # Frontend de la aplicación
│   ├── static/         # Archivos estáticos (CSS, JS, imágenes)
│   │   ├── css/        # Hojas de estilo
│   │   ├── js/         # Scripts de JavaScript
│   │   └── images/     # Imágenes y recursos
│   └── templates/      # Plantillas HTML
├── src/                # Código fuente del backend
│   ├── api/            # Endpoints de la API
│   ├── core/           # Lógica principal
│   ├── models/         # Modelos de datos
│   └── utils/          # Utilidades
├── tests/              # Pruebas automatizadas
├── .dockerignore       # Archivos a ignorar en Docker
├── .env.example        # Variables de entorno de ejemplo
├── .gitignore          # Archivos a ignorar en Git
├── docker-compose.yml  # Configuración de Docker Compose
├── Dockerfile          # Configuración de Docker
├── requirements.txt    # Dependencias de Python
└── README.md           # Este archivo
```

## 🧪 Ejemplos de Uso

### Cálculo Básico de Bombeo
```python
# Ejemplo de código para cálculo de pérdidas
from pumping_station import PumpingStation

ps = PumpingStation(
    flow_rate=100,  # l/s
    pipe_diameter=200,  # mm
    pipe_length=1000,  # m
    material='pvc'
)

print(f"Pérdidas de carga: {ps.head_loss:.2f} m")
```

### Generación de Informes
```python
from pumping_station.reports import generate_report

report = generate_report(
    project_name="Proyecto Ejemplo",
    data=calculation_results,
    format='pdf'
)
```

## 📚 Documentación

Para documentación detallada, por favor visite nuestra [Wiki](https://github.com/tu-usuario/pumping-station-calculator/wiki).

### Guías
- [Guía de Usuario](docs/user-guide.md)
- [API Reference](docs/api-reference.md)
- [Despliegue en Producción](docs/deployment.md)

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Por favor lee nuestras [guías de contribución](CONTRIBUTING.md) para más detalles.

### Pasos para Contribuir
1. Haz un Fork del proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Haz commit de tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Haz push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Distribuido bajo la licencia MIT. Ver `LICENSE` para más información.

## 📞 Contacto

Equipo de Desarrollo - [@tuusuario](https://twitter.com/tuusuario) - email@ejemplo.com

Enlace al Proyecto: [https://github.com/tu-usuario/pumping-station-calculator](https://github.com/tu-usuario/pumping-station-calculator)

## 🙏 Agradecimientos

- [FastAPI](https://fastapi.tiangolo.com/)
- [Bootstrap](https://getbootstrap.com/)
- [Chart.js](https://www.chartjs.org/)
- [Docker](https://www.docker.com/)

---

<div align="center">
  <p>Hecho con ❤️ por el equipo de desarrollo</p>
  <img src="https://img.shields.io/github/license/tu-usuario/pumping-station-calculator" alt="License">
  <img src="https://img.shields.io/github/v/release/tu-usuario/pumping-station-calculator" alt="Release">
  <img src="https://img.shields.io/github/last-commit/tu-usuario/pumping-station-calculator" alt="Last commit">
</div>


