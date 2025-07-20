#!/usr/bin/env python3
"""
Script de prueba para verificar la generación de PDF
"""
import requests
import json

# Datos de prueba
test_data = {
    "project_name": "Proyecto de Prueba PDF",
    "project_location": "Ciudad de Prueba",
    "geometric_height": 25.0,
    "geometric_height_unit": "m",
    "flow_rate": 50.0,
    "flow_rate_unit": "l/s",
    "pipe_length": 150.0,
    "pipe_length_unit": "m",
    "pipe_diameter": 200.0,
    "pipe_diameter_unit": "mm",
    "pipe_material": "PVC",
    "pump_efficiency": 0.75,
    "valve_gate": 2,
    "valve_globe": 1,
    "valve_check": 1,
    "valve_butterfly": 0,
    "elbow_90": 4,
    "elbow_45": 2,
    "tee_flow": 1,
    "tee_branch": 0,
    "reducer": 1,
    "entrance": 1,
    "exit": 1
}

def test_pdf_generation():
    """Prueba la generación de PDF"""
    try:
        print("Enviando solicitud para generar PDF...")
        
        # Enviar solicitud POST
        response = requests.post(
            "http://localhost:8001/generate-report",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Content Type: {response.headers.get('content-type', 'N/A')}")
        print(f"Content Length: {len(response.content)} bytes")
        
        if response.status_code == 200:
            # Verificar si es un PDF válido
            if response.content.startswith(b'%PDF'):
                print("✅ PDF generado correctamente")
                
                # Guardar el PDF para verificación manual
                with open("test_output.pdf", "wb") as f:
                    f.write(response.content)
                print("📄 PDF guardado como 'test_output.pdf'")
                
                # Verificar estructura básica del PDF
                content_str = response.content.decode('latin-1', errors='ignore')
                if 'VMS HYDRAULICS' in content_str:
                    print("✅ Contenido de VMS HYDRAULICS encontrado")
                else:
                    print("⚠️  Contenido de VMS HYDRAULICS no encontrado")
                    
            else:
                print("❌ El archivo no es un PDF válido")
                print(f"Primeros 100 caracteres: {response.content[:100]}")
        else:
            print(f"❌ Error en la solicitud: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error: {error_data}")
            except:
                print(f"Respuesta: {response.text[:500]}")
                
    except Exception as e:
        print(f"❌ Error en la prueba: {str(e)}")

if __name__ == "__main__":
    test_pdf_generation()
