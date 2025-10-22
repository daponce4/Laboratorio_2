"""
Servidor de NRCs (Códigos de Registro de Curso)
Servidor simple y secuencial que valida materias/NRC
Puerto: 12346
"""

import socket
import csv
import json
import os

ARCHIVO_NRC = 'nrcs.csv'
HOST = '127.0.0.1'
PORT = 12346

def inicializar_nrc_csv():
    """Crea el archivo de NRCs si no existe con datos de ejemplo"""
    if not os.path.exists(ARCHIVO_NRC):
        with open(ARCHIVO_NRC, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['NRC', 'Materia'])
            # Datos de ejemplo
            writer.writerow(['MAT101', 'Matemáticas I'])
            writer.writerow(['MAT102', 'Matemáticas II'])
            writer.writerow(['FIS101', 'Física I'])
            writer.writerow(['FIS102', 'Física II'])
            writer.writerow(['QUI101', 'Química I'])
            writer.writerow(['PRG101', 'Programación I'])
            writer.writerow(['PRG102', 'Programación II'])
            writer.writerow(['BDD101', 'Base de Datos I'])
            writer.writerow(['RED101', 'Redes I'])
            writer.writerow(['SOP101', 'Sistemas Operativos'])
        print(f"[*] Archivo {ARCHIVO_NRC} creado con datos de ejemplo")

def listar_nrcs():
    """Lista todos los NRCs disponibles"""
    try:
        nrcs = []
        with open(ARCHIVO_NRC, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                nrcs.append(row)
        return {"status": "ok", "data": nrcs}
    except Exception as e:
        return {"status": "error", "mensaje": str(e)}

def buscar_nrc(nrc_codigo):
    """Busca un NRC específico"""
    try:
        with open(ARCHIVO_NRC, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['NRC'].upper() == nrc_codigo.upper():
                    return {"status": "ok", "data": row}
        return {"status": "error", "mensaje": f"NRC '{nrc_codigo}' no existe"}
    except Exception as e:
        return {"status": "error", "mensaje": str(e)}

def procesar_comando(comando_str):
    """Procesa comandos del cliente"""
    try:
        partes = comando_str.strip().split('|')
        
        if len(partes) < 1:
            return {"status": "error", "mensaje": "Comando inválido"}
        
        accion = partes[0].upper()
        
        if accion == "LISTAR":
            return listar_nrcs()
        elif accion == "BUSCAR" and len(partes) == 2:
            nrc_codigo = partes[1].strip()
            return buscar_nrc(nrc_codigo)
        else:
            return {"status": "error", "mensaje": "Comando no reconocido"}
            
    except Exception as e:
        return {"status": "error", "mensaje": str(e)}

def main():
    # Inicializar archivo CSV
    inicializar_nrc_csv()
    
    # Crear socket TCP
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        # Enlazar y escuchar
        server_socket.bind((HOST, PORT))
        server_socket.listen(5)
        print(f"[*] Servidor de NRCs escuchando en {HOST}:{PORT}")
        print(f"[*] Archivo de NRCs: {ARCHIVO_NRC}")
        print("[*] Esperando consultas...")
        print("[*] Presione Ctrl+C para detener\n")
        
        contador = 0
        
        while True:
            # Aceptar conexión
            client_socket, client_address = server_socket.accept()
            contador += 1
            
            try:
                # Recibir comando
                data = client_socket.recv(1024).decode('utf-8')
                
                if data:
                    print(f"[Consulta #{contador}] Desde {client_address}: {data}")
                    
                    # Procesar comando
                    respuesta = procesar_comando(data)
                    
                    # Enviar respuesta en JSON
                    client_socket.send(json.dumps(respuesta).encode('utf-8'))
                    
                    if respuesta['status'] == 'ok':
                        print(f"[Respuesta #{contador}] ✓ OK")
                    else:
                        print(f"[Respuesta #{contador}] ✗ {respuesta['mensaje']}")
                
            except Exception as e:
                print(f"[ERROR] Error procesando consulta: {e}")
            finally:
                client_socket.close()
                
    except KeyboardInterrupt:
        print("\n[!] Servidor de NRCs detenido por el usuario")
    except Exception as e:
        print(f"[ERROR] Error del servidor: {e}")
    finally:
        server_socket.close()
        print("[*] Servidor cerrado")

if __name__ == "__main__":
    main()
