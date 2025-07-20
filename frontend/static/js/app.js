// Modern Pumping Station Calculator JavaScript
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('calcForm');
    const submitBtn = form.querySelector('.modern-btn');
    
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        try {
            // Obtener valores del formulario
            const formData = {
                project_name: document.getElementById('project_name').value,
                project_location: document.getElementById('project_location').value,
                geometric_height: parseFloat(document.getElementById('geometric_height').value),
                geometric_height_unit: document.getElementById('geometric_height_unit').value,
                flow_rate: parseFloat(document.getElementById('flow_rate').value),
                flow_rate_unit: document.getElementById('flow_rate_unit').value,
                pipe_length: parseFloat(document.getElementById('pipe_length').value),
                pipe_length_unit: document.getElementById('pipe_length_unit').value,
                pipe_diameter: parseFloat(document.getElementById('pipe_diameter').value),
                pipe_diameter_unit: document.getElementById('pipe_diameter_unit').value,
                pipe_material: document.getElementById('pipe_material').value,
                pump_efficiency: parseFloat(document.getElementById('pump_efficiency').value) / 100,

                // Accesorios
                valve_gate: parseInt(document.getElementById('valve_gate').value) || 0,
                valve_butterfly: parseInt(document.getElementById('valve_butterfly').value) || 0,
                valve_check: parseInt(document.getElementById('valve_check').value) || 0,
                valve_globe: parseInt(document.getElementById('valve_globe').value) || 0,
                elbow_90: parseInt(document.getElementById('elbow_90').value) || 0,
                elbow_45: parseInt(document.getElementById('elbow_45').value) || 0
            };
            
            console.log('Datos del formulario:', formData);
            
            // Mostrar estado de carga con animación moderna
            showLoadingState();
            
            // Enviar datos al backend
            const response = await fetch('/calculate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            console.log('Datos recibidos:', data);
            
            // Mostrar resultados con animación
            displayResults(data);
            
            // Generar gráfico
            generateChart(data);
            
        } catch (error) {
            console.error('Error en el cálculo:', error);
            showError('Error al realizar el cálculo. Por favor, verifica los datos e intenta nuevamente.');
        } finally {
            hideLoadingState();
        }
    });
    
    function showLoadingState() {
        // Cambiar texto del botón
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Calculando...';
        submitBtn.disabled = true;
        
        // Añadir clase de carga a los campos de resultado
        const resultFields = ['total_head', 'friction_head_loss', 'minor_head_loss', 'power', 'velocity', 'reynolds', 'friction_factor', 'curve_equation'];
        resultFields.forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = 'Calculando...';
                element.style.opacity = '0.6';
            }
        });
    }
    
    function hideLoadingState() {
        // Restaurar botón
        submitBtn.innerHTML = '<i class="fas fa-calculator me-2"></i>Calcular Sistema de Bombeo';
        submitBtn.disabled = false;
        
        // Restaurar opacidad de los resultados
        const resultFields = ['total_head', 'friction_head_loss', 'minor_head_loss', 'power', 'velocity', 'reynolds', 'friction_factor', 'curve_equation'];
        resultFields.forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                element.style.opacity = '1';
            }
        });
    }
    
    function displayResults(data) {
        // Mostrar resultados con animación
        const resultItems = document.querySelectorAll('.modern-result-item');
        
        // Animar entrada de resultados
        resultItems.forEach((item, index) => {
            setTimeout(() => {
                item.style.transform = 'translateY(-10px)';
                setTimeout(() => {
                    item.style.transform = 'translateY(0)';
                }, 100);
            }, index * 50);
        });
        
        // Actualizar valores
        document.getElementById('total_head').textContent = data.total_head + ' m';
        document.getElementById('friction_head_loss').textContent = data.friction_head_loss + ' m';
        document.getElementById('minor_head_loss').textContent = data.minor_head_loss + ' m';
        document.getElementById('power').textContent = data.power_kw + ' kW (' + data.power_hp + ' HP)';
        document.getElementById('velocity').textContent = data.velocity + ' m/s';
        document.getElementById('reynolds').textContent = data.reynolds.toLocaleString();
        document.getElementById('friction_factor').textContent = data.friction_factor;
        document.getElementById('curve_equation').textContent = data.curve_equation;
    }
    
    function generateChart(data) {
        // Destruir gráfico anterior si existe
        if (window.pumpChart) {
            window.pumpChart.destroy();
        }
        
        const ctx = document.getElementById('pumpCurveChart').getContext('2d');
        
        // Preparar datos para el gráfico
        const curveData = data.pump_curve.map(point => ({
            x: point.flow_ls,
            y: point.head
        }));
        
        // Punto de operación (BEP)
        const operatingPoint = {
            x: data.flow_rate, // Ya viene en l/s desde el backend
            y: data.total_head
        };
        
        // Calcular curva del sistema
        const systemCurveData = [];
        const geometricHeight = data.geometric_height;
        const maxFlow = Math.max(...curveData.map(p => p.x));
        
        // Generar puntos de la curva del sistema: H = H_geo + K*Q^2
        // Donde K se calcula basándose en el punto de operación
        const K = (data.friction_head_loss + data.minor_head_loss) / Math.pow(data.flow_rate, 2);
        
        for (let i = 0; i <= 20; i++) {
            const flow = (i / 20) * maxFlow;
            const systemHead = geometricHeight + K * Math.pow(flow, 2);
            systemCurveData.push({
                x: flow,
                y: systemHead
            });
        }
        
        console.log('Punto de operación:', operatingPoint);
        console.log('Datos de la curva:', curveData.slice(0, 3)); // Primeros 3 puntos
        console.log('Altura geométrica:', geometricHeight);
        console.log('Coeficiente K del sistema:', K);
        console.log('Datos de la curva del sistema:', systemCurveData.slice(0, 3)); // Primeros 3 puntos
        
        window.pumpChart = new Chart(ctx, {
            type: 'line',
            data: {
                datasets: [{
                    label: 'Curva de la Bomba',
                    data: curveData,
                    borderColor: 'rgba(102, 126, 234, 1)',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 0,
                    pointHoverRadius: 6
                }, {
                    label: 'Curva del Sistema',
                    data: systemCurveData,
                    borderColor: 'rgba(40, 167, 69, 1)',
                    backgroundColor: 'rgba(40, 167, 69, 0.1)',
                    borderWidth: 3,
                    fill: false,
                    tension: 0.4,
                    pointRadius: 0,
                    pointHoverRadius: 6,
                    borderDash: [5, 5]
                }, {
                    label: 'Punto de Operación',
                    data: [operatingPoint],
                    backgroundColor: 'rgba(245, 87, 108, 1)',
                    borderColor: 'rgba(245, 87, 108, 1)',
                    pointRadius: 10,
                    pointHoverRadius: 12,
                    showLine: false,
                    type: 'scatter'
                }, {
                    label: 'Línea de Referencia Horizontal',
                    data: [{x: 0, y: operatingPoint.y}, {x: operatingPoint.x, y: operatingPoint.y}],
                    borderColor: 'rgba(220, 53, 69, 1)',
                    borderWidth: 3,
                    borderDash: [10, 5],
                    pointRadius: 0,
                    fill: false,
                    tension: 0,
                    type: 'line'
                }, {
                    label: 'Línea de Referencia Vertical',
                    data: [{x: operatingPoint.x, y: 0}, {x: operatingPoint.x, y: operatingPoint.y}],
                    borderColor: 'rgba(220, 53, 69, 1)',
                    borderWidth: 3,
                    borderDash: [10, 5],
                    pointRadius: 0,
                    fill: false,
                    tension: 0,
                    type: 'line'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: false
                    },
                    legend: {
                        display: true,
                        position: 'top',
                        labels: {
                            usePointStyle: true,
                            padding: 20,
                            font: {
                                family: 'Inter',
                                size: 12
                            },
                            filter: function(item, chart) {
                                // Ocultar las líneas de referencia de la leyenda
                                return !item.text.includes('Línea de Referencia');
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        type: 'linear',
                        position: 'bottom',
                        title: {
                            display: true,
                            text: 'Caudal (l/s)',
                            font: {
                                family: 'Inter',
                                size: 14,
                                weight: '500'
                            }
                        },
                        grid: {
                            color: 'rgba(0,0,0,0.1)'
                        }
                    },
                    y: {
                        type: 'linear',
                        title: {
                            display: true,
                            text: 'Altura (m)',
                            font: {
                                family: 'Inter',
                                size: 14,
                                weight: '500'
                            }
                        },
                        grid: {
                            color: 'rgba(0,0,0,0.1)'
                        }
                    }
                },
                interaction: {
                    intersect: false,
                    mode: 'index'
                },
                animation: {
                    duration: 1000,
                    easing: 'easeInOutQuart'
                }
            }
        });
    }
    
    function showError(message) {
        // Crear notificación de error moderna
        const errorDiv = document.createElement('div');
        errorDiv.className = 'alert alert-danger alert-dismissible fade show position-fixed';
        errorDiv.style.cssText = `
            top: 20px;
            right: 20px;
            z-index: 1050;
            max-width: 400px;
            border-radius: 12px;
            box-shadow: 0 10px 25px rgba(220, 53, 69, 0.3);
        `;
        errorDiv.innerHTML = `
            <i class="fas fa-exclamation-triangle me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(errorDiv);
        
        // Auto-remover después de 5 segundos
        setTimeout(() => {
            if (errorDiv.parentNode) {
                errorDiv.remove();
            }
        }, 5000);
    }
    
    // Añadir efectos hover a los campos de entrada
    const inputs = document.querySelectorAll('.modern-input, .modern-select');
    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.parentElement.style.transform = 'translateY(-2px)';
        });
        
        input.addEventListener('blur', function() {
            this.parentElement.style.transform = 'translateY(0)';
        });
    });
    
    // Event listener for PDF generation button
    document.getElementById('generate-pdf').addEventListener('click', async () => {
        console.log('PDF button clicked');
        
        const formData = {
            project_name: document.getElementById('project_name').value,
            project_location: document.getElementById('project_location').value,
            geometric_height: parseFloat(document.getElementById('geometric_height').value),
            geometric_height_unit: document.getElementById('geometric_height_unit').value,
            flow_rate: parseFloat(document.getElementById('flow_rate').value),
            flow_rate_unit: document.getElementById('flow_rate_unit').value,
            pipe_length: parseFloat(document.getElementById('pipe_length').value),
            pipe_length_unit: document.getElementById('pipe_length_unit').value,
            pipe_diameter: parseFloat(document.getElementById('pipe_diameter').value),
            pipe_diameter_unit: document.getElementById('pipe_diameter_unit').value,
            pipe_material: document.getElementById('pipe_material').value,
            pump_efficiency: parseFloat(document.getElementById('pump_efficiency').value) / 100,

            // Accesorios
            valve_gate: parseInt(document.getElementById('valve_gate').value) || 0,
            valve_butterfly: parseInt(document.getElementById('valve_butterfly').value) || 0,
            valve_check: parseInt(document.getElementById('valve_check').value) || 0,
            valve_globe: parseInt(document.getElementById('valve_globe').value) || 0,
            elbow_90: parseInt(document.getElementById('elbow_90').value) || 0,
            elbow_45: parseInt(document.getElementById('elbow_45').value) || 0
        };
        console.log('Form data:', formData);
        
        try {
            const response = await fetch('/generate-report', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });

            if (!response.ok) throw new Error('Error en generación de PDF');
            
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'reporte_bombeo.pdf';
            document.body.appendChild(a);
            a.click();
            a.remove();
        } catch (error) {
            console.error('Error:', error);
            alert('Error generando PDF: ' + error.message);
        }
    });
});
