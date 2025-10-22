"""
Cliente TCP - Laboratorio 2
Aplicaciones Distribuidas
Sistema de gestión de calificaciones
"""

import socket
import json

def mostrar_menu():
    """Muestra el menú de opciones"""
    print("\n" + "="*50)
    print("SISTEMA DE GESTIÓN DE CALIFICACIONES")
    print("="*50)
    print("1. Agregar calificación")
    print("2. Listar todas las calificaciones")
    print("3. Buscar calificaciones por ID")
    print("4. Actualizar calificación")
    print("5. Eliminar calificación")
    print("6. Salir")
    print("="*50)

def agregar_calificacion():
    """Solicita datos para agregar una calificación"""
    print("\n--- AGREGAR CALIFICACIÓN ---")
    id_est = input("ID del estudiante: ")
    nombre = input("Nombre del estudiante: ")
    materia = input("Materia: ")
    calificacion = input("Calificación: ")
    
    comando = {
        "accion": "agregar",
        "datos": {
            "id": id_est,
            "nombre": nombre,
            "materia": materia,
            "calificacion": calificacion
        }
    }
    return json.dumps(comando)

def listar_calificaciones():
    """Solicita listar todas las calificaciones"""
    comando = {
        "accion": "listar"
    }
    return json.dumps(comando)

def buscar_calificacion():
    """Solicita buscar calificaciones por ID"""
    print("\n--- BUSCAR CALIFICACIÓN ---")
    id_est = input("ID del estudiante: ")
    
    comando = {
        "accion": "buscar",
        "datos": {
            "id": id_est
        }
    }
    return json.dumps(comando)

def actualizar_calificacion():
    """Solicita datos para actualizar una calificación"""
    print("\n--- ACTUALIZAR CALIFICACIÓN ---")
    id_est = input("ID del estudiante: ")
    materia = input("Materia: ")
    nueva_calificacion = input("Nueva calificación: ")
    
    comando = {
        "accion": "actualizar",
        "datos": {
            "id": id_est,
            "materia": materia,
            "calificacion": nueva_calificacion
        }
    }
    return json.dumps(comando)

def eliminar_calificacion():
    """Solicita datos para eliminar una calificación"""
    print("\n--- ELIMINAR CALIFICACIÓN ---")
    id_est = input("ID del estudiante: ")
    materia = input("Materia: ")
    
    comando = {
        "accion": "eliminar",
        "datos": {
            "id": id_est,
            "materia": materia
        }
    }
    return json.dumps(comando)

def mostrar_respuesta(respuesta_json):
    """Muestra la respuesta del servidor de forma legible"""
    try:
        respuesta = json.loads(respuesta_json)
        
        if respuesta['status'] == 'success':
            print("\n✓ ÉXITO:", respuesta.get('mensaje', ''))
            
            if 'data' in respuesta:
                print("\nDatos:")
                if isinstance(respuesta['data'], list):
                    if len(respuesta['data']) == 0:
                        print("  No hay registros")
                    else:
                        for i, item in enumerate(respuesta['data'], 1):
                            print(f"\n  Registro {i}:")
                            for key, value in item.items():
                                print(f"    {key}: {value}")
                else:
                    print(f"  {respuesta['data']}")
        else:
            print("\n✗ ERROR:", respuesta.get('mensaje', 'Error desconocido'))
            
    except json.JSONDecodeError:
        print("\n✗ ERROR: Respuesta del servidor no válida")
    except Exception as e:
        print(f"\n✗ ERROR: {e}")

def main():
    # Configuración del cliente
    HOST = '127.0.0.1'
    PORT = 5000
    
    # Crear socket TCP
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        # Conectar al servidor
        client_socket.connect((HOST, PORT))
        print(f"[+] Conectado al servidor {HOST}:{PORT}")
        
        while True:
            mostrar_menu()
            opcion = input("\nSeleccione una opción: ")
            
            if opcion == '1':
                comando = agregar_calificacion()
            elif opcion == '2':
                comando = listar_calificaciones()
            elif opcion == '3':
                comando = buscar_calificacion()
            elif opcion == '4':
                comando = actualizar_calificacion()
            elif opcion == '5':
                comando = eliminar_calificacion()
            elif opcion == '6':
                print("\n[!] Cerrando conexión...")
                break
            else:
                print("\n✗ Opción no válida")
                continue
            
            try:
                # Enviar comando al servidor
                client_socket.send(comando.encode('utf-8'))
                
                # Recibir respuesta
                respuesta = client_socket.recv(4096).decode('utf-8')
                
                # Mostrar respuesta
                mostrar_respuesta(respuesta)
                
                input("\nPresione Enter para continuar...")
                
            except Exception as e:
                print(f"\n[ERROR] Error en comunicación: {e}")
                break
        
    except ConnectionRefusedError:
        print(f"\n[ERROR] No se pudo conectar al servidor {HOST}:{PORT}")
        print("[!] Asegúrate de que el servidor esté ejecutándose")
    except Exception as e:
        print(f"\n[ERROR] Error del cliente: {e}")
    finally:
        client_socket.close()
        print("[*] Cliente desconectado")

if __name__ == "__main__":
    main()
