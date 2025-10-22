"""
Servidor TCP con hilos - Laboratorio 2
Aplicaciones Distribuidas
Maneja múltiples clientes simultáneamente usando threading
Sistema de gestión de calificaciones con validación de NRC
"""

import socket
import csv
import json
import os
import threading

ARCHIVO_CSV = 'calificaciones_hilos.csv'
archivo_lock = threading.Lock()  # Lock para acceso concurrente al archivo

# Configuración del servidor de NRCs
NRC_SERVER_HOST = '127.0.0.1'
NRC_SERVER_PORT = 12346

# Función para consultar el servidor de NRCs
def consultar_nrc(nrc):
    """
    Consulta al servidor de NRCs si un código es válido
    Retorna: dict con status 'ok' o 'error'
    """
    try:
        # Crear socket para consultar al servidor de NRCs
        nrc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        nrc_socket.settimeout(5)  # Timeout de 5 segundos
        
        # Conectar al servidor de NRCs
        nrc_socket.connect((NRC_SERVER_HOST, NRC_SERVER_PORT))
        
        # Enviar comando de búsqueda
        comando = f"BUSCAR|{nrc}"
        nrc_socket.send(comando.encode('utf-8'))
        
        # Recibir respuesta
        respuesta = nrc_socket.recv(1024).decode('utf-8')
        resultado = json.loads(respuesta)
        
        # Cerrar conexión
        nrc_socket.close()
        
        return resultado
        
    except socket.timeout:
        return {"status": "error", "mensaje": "Timeout consultando servidor de NRCs"}
    except ConnectionRefusedError:
        return {"status": "error", "mensaje": "Error: Servidor de NRCs no disponible"}
    except Exception as e:
        return {"status": "error", "mensaje": f"Error consultando NRC: {str(e)}"}

# Funciones para manejo de CSV
def inicializar_csv():
    """Crea el archivo CSV si no existe"""
    if not os.path.exists(ARCHIVO_CSV):
        with archivo_lock:
            with open(ARCHIVO_CSV, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['ID', 'Nombre', 'Materia', 'Calificacion'])
        print(f"[*] Archivo {ARCHIVO_CSV} creado")

def agregar_calificacion(datos):
    """Agrega una nueva calificación al CSV (thread-safe) con validación de NRC"""
    try:
        # VALIDAR NRC ANTES DE AGREGAR
        nrc = datos.get('materia', '')
        print(f"[Validación] Consultando NRC: {nrc}")
        
        res_nrc = consultar_nrc(nrc)
        
        if res_nrc["status"] != "ok":
            print(f"[Validación] ✗ NRC inválido: {nrc}")
            return {"status": "error", "mensaje": f"Materia/NRC no válida: {res_nrc.get('mensaje', 'NRC no existe')}"}
        
        print(f"[Validación] ✓ NRC válido: {nrc} - {res_nrc['data']['Materia']}")
        
        # Si el NRC es válido, agregar la calificación
        with archivo_lock:
            with open(ARCHIVO_CSV, 'a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([datos['id'], datos['nombre'], datos['materia'], datos['calificacion']])
        
        return {"status": "success", "mensaje": f"Calificación agregada correctamente (NRC: {nrc} - {res_nrc['data']['Materia']})"}
        
    except Exception as e:
        return {"status": "error", "mensaje": str(e)}

def listar_calificaciones():
    """Lista todas las calificaciones (thread-safe)"""
    try:
        calificaciones = []
        with archivo_lock:
            with open(ARCHIVO_CSV, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    calificaciones.append(row)
        return {"status": "success", "data": calificaciones}
    except Exception as e:
        return {"status": "error", "mensaje": str(e)}

def buscar_calificacion(id_estudiante):
    """Busca calificaciones por ID de estudiante (thread-safe)"""
    try:
        resultados = []
        with archivo_lock:
            with open(ARCHIVO_CSV, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row['ID'] == id_estudiante:
                        resultados.append(row)
        
        if resultados:
            return {"status": "success", "data": resultados}
        else:
            return {"status": "error", "mensaje": "No se encontraron calificaciones para ese ID"}
    except Exception as e:
        return {"status": "error", "mensaje": str(e)}

def actualizar_calificacion(datos):
    """Actualiza una calificación existente (thread-safe) con validación de NRC si cambia"""
    try:
        # Si se está cambiando la materia, validar el nuevo NRC
        nueva_materia = datos.get('nueva_materia')
        if nueva_materia:
            print(f"[Validación] Consultando nuevo NRC: {nueva_materia}")
            res_nrc = consultar_nrc(nueva_materia)
            
            if res_nrc["status"] != "ok":
                print(f"[Validación] ✗ NRC inválido: {nueva_materia}")
                return {"status": "error", "mensaje": f"Nuevo NRC no válido: {res_nrc.get('mensaje', 'NRC no existe')}"}
            
            print(f"[Validación] ✓ Nuevo NRC válido: {nueva_materia} - {res_nrc['data']['Materia']}")
        
        calificaciones = []
        actualizado = False
        
        with archivo_lock:
            with open(ARCHIVO_CSV, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                calificaciones = list(reader)
            
            for cal in calificaciones:
                if cal['ID'] == datos['id'] and cal['Materia'] == datos['materia']:
                    cal['Calificacion'] = datos['calificacion']
                    # Si hay nueva materia, actualizarla
                    if nueva_materia:
                        cal['Materia'] = nueva_materia
                        mensaje_extra = f" (Nuevo NRC: {nueva_materia} - {res_nrc['data']['Materia']})"
                    else:
                        mensaje_extra = ""
                    actualizado = True
                    break
            
            if actualizado:
                with open(ARCHIVO_CSV, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.DictWriter(file, fieldnames=['ID', 'Nombre', 'Materia', 'Calificacion'])
                    writer.writeheader()
                    writer.writerows(calificaciones)
        
        if actualizado:
            return {"status": "success", "mensaje": f"Calificación actualizada correctamente{mensaje_extra if nueva_materia else ''}"}
        else:
            return {"status": "error", "mensaje": "No se encontró la calificación a actualizar"}
    except Exception as e:
        return {"status": "error", "mensaje": str(e)}

def eliminar_calificacion(datos):
    """Elimina una calificación (thread-safe)"""
    try:
        calificaciones = []
        eliminado = False
        
        with archivo_lock:
            with open(ARCHIVO_CSV, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                calificaciones = list(reader)
            
            calificaciones_filtradas = []
            for cal in calificaciones:
                if not (cal['ID'] == datos['id'] and cal['Materia'] == datos['materia']):
                    calificaciones_filtradas.append(cal)
                else:
                    eliminado = True
            
            if eliminado:
                with open(ARCHIVO_CSV, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.DictWriter(file, fieldnames=['ID', 'Nombre', 'Materia', 'Calificacion'])
                    writer.writeheader()
                    writer.writerows(calificaciones_filtradas)
        
        if eliminado:
            return {"status": "success", "mensaje": "Calificación eliminada correctamente"}
        else:
            return {"status": "error", "mensaje": "No se encontró la calificación a eliminar"}
    except Exception as e:
        return {"status": "error", "mensaje": str(e)}

def procesar_comando(comando_json):
    """Procesa el comando recibido del cliente"""
    try:
        comando = json.loads(comando_json)
        accion = comando.get('accion')
        
        if accion == 'agregar':
            return agregar_calificacion(comando['datos'])
        elif accion == 'listar':
            return listar_calificaciones()
        elif accion == 'buscar':
            return buscar_calificacion(comando['datos']['id'])
        elif accion == 'actualizar':
            return actualizar_calificacion(comando['datos'])
        elif accion == 'eliminar':
            return eliminar_calificacion(comando['datos'])
        else:
            return {"status": "error", "mensaje": "Acción no válida"}
    except json.JSONDecodeError:
        return {"status": "error", "mensaje": "Formato JSON inválido"}
    except Exception as e:
        return {"status": "error", "mensaje": str(e)}

def manejar_cliente(client_socket, client_address, client_id):
    """Maneja la comunicación con un cliente específico (ejecutado en un hilo)"""
    print(f"[+] Cliente {client_id} conectado desde {client_address}")
    
    try:
        while True:
            # Recibir comando del cliente
            data = client_socket.recv(4096).decode('utf-8')
            
            if not data:
                print(f"[!] Cliente {client_id} desconectado")
                break
            
            print(f"[Cliente {client_id}] Comando recibido: {data[:50]}...")
            
            # Procesar comando
            respuesta = procesar_comando(data)
            
            # Enviar respuesta
            client_socket.send(json.dumps(respuesta).encode('utf-8'))
            print(f"[Cliente {client_id}] Respuesta enviada")
            
    except Exception as e:
        print(f"[ERROR] Error con cliente {client_id}: {e}")
    finally:
        client_socket.close()
        print(f"[*] Conexión con cliente {client_id} cerrada")

def main():
    # Inicializar archivo CSV
    inicializar_csv()
    
    # Configuración del servidor
    HOST = '127.0.0.1'
    PORT = 5001  # Puerto diferente para no conflictuar con el servidor sin hilos
    
    # Crear socket TCP
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        # Enlazar y escuchar
        server_socket.bind((HOST, PORT))
        server_socket.listen(5)  # Hasta 5 clientes en cola
        print(f"[*] Servidor CON HILOS escuchando en {HOST}:{PORT}")
        print("[*] Esperando conexiones de clientes...")
        print("[*] Presione Ctrl+C para detener el servidor\n")
        
        client_counter = 0
        
        while True:
            # Aceptar conexión
            client_socket, client_address = server_socket.accept()
            client_counter += 1
            
            # Crear un nuevo hilo para manejar este cliente
            client_thread = threading.Thread(
                target=manejar_cliente,
                args=(client_socket, client_address, client_counter)
            )
            client_thread.daemon = True  # El hilo se cierra cuando el programa principal termina
            client_thread.start()
            
            print(f"[*] Clientes activos: {threading.active_count() - 1}")
        
    except KeyboardInterrupt:
        print("\n[!] Servidor detenido por el usuario")
    except Exception as e:
        print(f"[ERROR] Error del servidor: {e}")
    finally:
        server_socket.close()
        print("[*] Servidor cerrado")

if __name__ == "__main__":
    main()
