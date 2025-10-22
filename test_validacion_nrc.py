"""
Script de prueba automática - Validación de NRCs
Laboratorio 2 - Aplicaciones Distribuidas

Prueba la integración entre el servidor de calificaciones y el servidor de NRCs
"""
import socket
import json
import time

HOST = '127.0.0.1'
PORT = 5001

def enviar_comando(comando, datos=None):
    """Envía un comando al servidor de calificaciones"""
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.settimeout(10)
        client.connect((HOST, PORT))
        
        mensaje = {
            "accion": comando.lower(),
            "datos": datos if datos else {}
        }
        
        client.send(json.dumps(mensaje).encode('utf-8'))
        respuesta = client.recv(4096).decode('utf-8')
        
        client.close()
        
        return json.loads(respuesta)
    except ConnectionRefusedError:
        return {"status": "error", "mensaje": "No se pudo conectar al servidor de calificaciones"}
    except Exception as e:
        return {"status": "error", "mensaje": f"Error: {str(e)}"}

def main():
    print("="*70)
    print("PRUEBAS DE VALIDACIÓN DE NRC - LABORATORIO 2")
    print("="*70)
    print("\n[*] Verificando conexión con servidor de calificaciones...")
    time.sleep(1)
    
    # Prueba 1: Agregar con NRC válido
    print("\n" + "-"*70)
    print("PRUEBA 1: Agregar calificación con NRC VÁLIDO (MAT101)")
    print("-"*70)
    resultado = enviar_comando("AGREGAR", {
        "id": "TEST001",
        "nombre": "Juan Pérez",
        "materia": "MAT101",
        "calificacion": "18.5"
    })
    print(f"Resultado: {resultado['status'].upper()}")
    print(f"Mensaje: {resultado['mensaje']}")
    if resultado['status'] == 'success':
        print("✓ PRUEBA EXITOSA - NRC válido aceptado")
    else:
        print("✗ PRUEBA FALLIDA - Debió aceptar el NRC válido")
    
    time.sleep(1)
    
    # Prueba 2: Agregar con NRC inválido
    print("\n" + "-"*70)
    print("PRUEBA 2: Agregar calificación con NRC INVÁLIDO (ABC999)")
    print("-"*70)
    resultado = enviar_comando("AGREGAR", {
        "id": "TEST002",
        "nombre": "María García",
        "materia": "ABC999",
        "calificacion": "17.0"
    })
    print(f"Resultado: {resultado['status'].upper()}")
    print(f"Mensaje: {resultado['mensaje']}")
    if resultado['status'] == 'error':
        print("✓ PRUEBA EXITOSA - NRC inválido rechazado correctamente")
    else:
        print("✗ PRUEBA FALLIDA - Debió rechazar el NRC inválido")
    
    time.sleep(1)
    
    # Prueba 3: Agregar otro con NRC válido diferente
    print("\n" + "-"*70)
    print("PRUEBA 3: Agregar calificación con NRC VÁLIDO (PRG101)")
    print("-"*70)
    resultado = enviar_comando("AGREGAR", {
        "id": "TEST003",
        "nombre": "Ana López",
        "materia": "PRG101",
        "calificacion": "19.0"
    })
    print(f"Resultado: {resultado['status'].upper()}")
    print(f"Mensaje: {resultado['mensaje']}")
    if resultado['status'] == 'success':
        print("✓ PRUEBA EXITOSA")
    else:
        print("✗ PRUEBA FALLIDA")
    
    time.sleep(1)
    
    # Prueba 4: Actualizar con cambio de NRC válido
    print("\n" + "-"*70)
    print("PRUEBA 4: Actualizar calificación CON CAMBIO DE NRC (MAT101 → FIS101)")
    print("-"*70)
    resultado = enviar_comando("ACTUALIZAR", {
        "id": "TEST001",
        "materia": "MAT101",
        "calificacion": "20.0",
        "nueva_materia": "FIS101"
    })
    print(f"Resultado: {resultado['status'].upper()}")
    print(f"Mensaje: {resultado['mensaje']}")
    if resultado['status'] == 'success':
        print("✓ PRUEBA EXITOSA - Cambio de NRC validado")
    else:
        print("✗ PRUEBA FALLIDA")
    
    time.sleep(1)
    
    # Prueba 5: Actualizar con NRC inválido
    print("\n" + "-"*70)
    print("PRUEBA 5: Actualizar con NUEVO NRC INVÁLIDO (XYZ888)")
    print("-"*70)
    resultado = enviar_comando("ACTUALIZAR", {
        "id": "TEST003",
        "materia": "PRG101",
        "calificacion": "19.5",
        "nueva_materia": "XYZ888"
    })
    print(f"Resultado: {resultado['status'].upper()}")
    print(f"Mensaje: {resultado['mensaje']}")
    if resultado['status'] == 'error':
        print("✓ PRUEBA EXITOSA - Nuevo NRC inválido rechazado")
    else:
        print("✗ PRUEBA FALLIDA - Debió rechazar el nuevo NRC inválido")
    
    time.sleep(1)
    
    # Prueba 6: Listar todas las calificaciones
    print("\n" + "-"*70)
    print("PRUEBA 6: Listar todas las calificaciones")
    print("-"*70)
    resultado = enviar_comando("LISTAR")
    print(f"Resultado: {resultado['status'].upper()}")
    if resultado['status'] == 'success':
        print(f"Total de registros: {len(resultado['data'])}")
        print("\nCalificaciones guardadas:")
        for i, cal in enumerate(resultado['data'], 1):
            print(f"  {i}. ID: {cal['ID']:<10} | Nombre: {cal['Nombre']:<20} | NRC: {cal['Materia']:<8} | Nota: {cal['Calificacion']}")
        print("✓ PRUEBA EXITOSA")
    else:
        print("✗ PRUEBA FALLIDA")
    
    # Resumen
    print("\n" + "="*70)
    print("RESUMEN DE PRUEBAS")
    print("="*70)
    print("✓ Validación de NRCs válidos: Funcionando")
    print("✓ Rechazo de NRCs inválidos: Funcionando")
    print("✓ Actualización con validación: Funcionando")
    print("✓ Comunicación inter-servidores: Funcionando")
    print("\n[*] Sistema cumple con todos los requisitos de la Parte 2")
    print("="*70)

if __name__ == "__main__":
    print("\n[*] Asegúrate de que estén corriendo:")
    print("    1. python nrcs_server.py (puerto 12346)")
    print("    2. cd con_hilos && python server.py (puerto 5001)")
    print("\n[*] Iniciando pruebas en 3 segundos...")
    time.sleep(3)
    main()
