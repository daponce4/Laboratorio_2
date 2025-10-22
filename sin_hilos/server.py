"""
Servidor TCP sin hilos - Laboratorio 2
Aplicaciones Distribuidas
Maneja un solo cliente a la vez
Sistema de gestión de calificaciones
"""

import socket
import csv
import json
import os

ARCHIVO_CSV = 'calificaciones.csv'

# Funciones para manejo de CSV
def inicializar_csv():
    """Crea el archivo CSV si no existe"""
    if not os.path.exists(ARCHIVO_CSV):
        with open(ARCHIVO_CSV, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['ID', 'Nombre', 'Materia', 'Calificacion'])
        print(f"[*] Archivo {ARCHIVO_CSV} creado")

def agregar_calificacion(datos):
    """Agrega una nueva calificación al CSV"""
    try:
        with open(ARCHIVO_CSV, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([datos['id'], datos['nombre'], datos['materia'], datos['calificacion']])
        return {"status": "success", "mensaje": "Calificación agregada correctamente"}
    except Exception as e:
        return {"status": "error", "mensaje": str(e)}

def listar_calificaciones():
    """Lista todas las calificaciones"""
    try:
        calificaciones = []
        with open(ARCHIVO_CSV, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                calificaciones.append(row)
        return {"status": "success", "data": calificaciones}
    except Exception as e:
        return {"status": "error", "mensaje": str(e)}

def buscar_calificacion(id_estudiante):
    """Busca calificaciones por ID de estudiante"""
    try:
        resultados = []
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
    """Actualiza una calificación existente"""
    try:
        calificaciones = []
        actualizado = False
        
        with open(ARCHIVO_CSV, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            calificaciones = list(reader)
        
        for cal in calificaciones:
            if cal['ID'] == datos['id'] and cal['Materia'] == datos['materia']:
                cal['Calificacion'] = datos['calificacion']
                actualizado = True
                break
        
        if actualizado:
            with open(ARCHIVO_CSV, 'w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=['ID', 'Nombre', 'Materia', 'Calificacion'])
                writer.writeheader()
                writer.writerows(calificaciones)
            return {"status": "success", "mensaje": "Calificación actualizada correctamente"}
        else:
            return {"status": "error", "mensaje": "No se encontró la calificación a actualizar"}
    except Exception as e:
        return {"status": "error", "mensaje": str(e)}

def eliminar_calificacion(datos):
    """Elimina una calificación"""
    try:
        calificaciones = []
        eliminado = False
        
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

def main():
    # Inicializar archivo CSV
    inicializar_csv()
    
    # Configuración del servidor
    HOST = '127.0.0.1'
    PORT = 5000
    
    # Crear socket TCP
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        # Enlazar y escuchar
        server_socket.bind((HOST, PORT))
        server_socket.listen(1)
        print(f"[*] Servidor SIN HILOS escuchando en {HOST}:{PORT}")
        print("[*] Esperando conexión del cliente...")
        
        # Aceptar conexión
        client_socket, client_address = server_socket.accept()
        print(f"[+] Cliente conectado desde {client_address}")
        
        # Comunicación con el cliente
        while True:
            try:
                # Recibir comando del cliente
                data = client_socket.recv(4096).decode('utf-8')
                
                if not data:
                    print("[!] Cliente desconectado")
                    break
                
                print(f"[*] Comando recibido: {data}")
                
                # Procesar comando
                respuesta = procesar_comando(data)
                
                # Enviar respuesta
                client_socket.send(json.dumps(respuesta).encode('utf-8'))
                
            except Exception as e:
                print(f"[ERROR] Error en comunicación: {e}")
                break
        
        client_socket.close()
        print("[*] Conexión cerrada")
        
    except Exception as e:
        print(f"[ERROR] Error del servidor: {e}")
    finally:
        server_socket.close()
        print("[*] Servidor detenido")

if __name__ == "__main__":
    main()