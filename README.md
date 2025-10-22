# Laboratorio 2 - Aplicaciones Distribuidas con IP
## Sistema de Gestión de Calificaciones (Cliente-Servidor TCP)

Sistema cliente-servidor que permite gestionar calificaciones de estudiantes mediante sockets TCP. Implementado en dos versiones: sin hilos (un cliente) y con hilos (múltiples clientes).

---

## Estructura del Proyecto

```
Laboratorio_2/
├── sin_hilos/
│   ├── server.py          # Servidor sin threading (1 cliente)
│   └── client.py          # Cliente para servidor sin hilos
│
├── con_hilos/
│   ├── server.py          # Servidor con threading (múltiples clientes)
│   └── client.py          # Cliente para servidor con hilos
│
└── README.md              # Este archivo
```

---

## Características

### Versión SIN HILOS (`sin_hilos/`)
- **Puerto:** 5000
- **Capacidad:** 1 cliente a la vez
- **Modelo:** Secuencial/Bloqueante
- **Archivo:** `calificaciones.csv`
- **Validación NRC:** No implementada

### Versión CON HILOS (`con_hilos/`)
- **Puerto:** 5001
- **Capacidad:** Múltiples clientes simultáneos
- **Modelo:** Concurrente con threading
- **Archivo:** `calificaciones_hilos.csv`
- **Validación NRC:** ACTIVA (consulta servidor en puerto 12346)

### Servidor de NRCs (`nrcs_server.py`)
- **Puerto:** 12346
- **Función:** Validar códigos NRC de materias
- **Archivo:** `nrcs.csv`
- **Comandos:**
  - `LISTAR` - Lista todos los NRCs disponibles
  - `BUSCAR|<NRC>` - Valida un NRC específico

---

## Funcionalidades (CRUD)

| Operación | Descripción | Validación NRC (con_hilos) |
|-----------|-------------|---------------------------|
| **Agregar** | Registrar nueva calificación (ID, Nombre, NRC, Nota) | SI |
| **Listar** | Mostrar todas las calificaciones | NO |
| **Buscar** | Buscar calificaciones por ID de estudiante | NO |
| **Actualizar** | Modificar calificación y/o cambiar NRC | SI (si cambia NRC) |
| **Eliminar** | Eliminar registro de calificación | NO |

---

## Instrucciones de Ejecución

### Servidor SIN HILOS

**Terminal 1 - Servidor:**
```bash
cd sin_hilos
python server.py
```

**Terminal 2 - Cliente:**
```bash
cd sin_hilos
python client.py
```

### Servidor CON HILOS (con validación de NRCs)

**IMPORTANTE:** Debe iniciarse en este orden:

**Terminal 1 - Servidor de NRCs (PRIMERO):**
```bash
python nrcs_server.py
```
*Salida esperada: `[*] Servidor de NRCs escuchando en 127.0.0.1:12346`*

**Terminal 2 - Servidor de Calificaciones:**
```bash
cd con_hilos
python server.py
```
*Salida esperada: `[*] Validación de NRCs: ACTIVA (puerto 12346)`*

**Terminales 3, 4, 5... - Clientes:**
```bash
cd con_hilos
python client.py
```
*Puedes abrir múltiples clientes simultáneamente*

---

## Protocolo de Comunicación

### Formato JSON

**Comando del cliente (Agregar con NRC válido):**
```json
{
  "accion": "agregar",
  "datos": {
    "id": "001",
    "nombre": "Juan Pérez",
    "materia": "MAT101",
    "calificacion": "95"
  }
}
```

**Respuesta del servidor (éxito):**
```json
{
  "status": "success",
  "mensaje": "Calificación agregada correctamente (NRC: MAT101 - Matemáticas I)"
}
```

**Respuesta del servidor (NRC inválido):**
```json
{
  "status": "error",
  "mensaje": "NRC no válido: NRC no existe en la base de datos"
}
```

**Respuesta del servidor (Servidor NRC caído):**
```json
{
  "status": "error",
  "mensaje": "Error: Servidor de NRCs no disponible"
}
```

---

## Arquitectura de Microservicios (Parte 2)

```
┌─────────────┐         ┌──────────────────────┐         ┌─────────────────┐
│   Cliente   │────────>│  Servidor de         │────────>│  Servidor de    │
│             │  JSON   │  Calificaciones      │ BUSCAR  │  NRCs           │
│  (Puerto    │         │  (Puerto 5001)       │ |NRC|   │  (Puerto 12346) │
│   client)   │<────────│                      │<────────│                 │
└─────────────┘  JSON   │  - CRUD Operaciones  │  JSON   │  - Validación   │
                        │  - Thread-safe       │         │  - nrcs.csv     │
                        │  - calificaciones_   │         └─────────────────┘
                        │    hilos.csv         │
                        └──────────────────────┘
```

### NRCs Válidos Disponibles

| NRC | Materia |
|-----|---------|
| MAT101 | Matemáticas I |
| MAT102 | Matemáticas II |
| FIS101 | Física I |
| FIS102 | Física II |
| QUI101 | Química I |
| PRG101 | Programación I |
| PRG102 | Programación II |
| BDD101 | Base de Datos I |
| RED101 | Redes I |
| SOP101 | Sistemas Operativos |

---

## Comparación Entre Versiones

| Característica | Sin Hilos | Con Hilos |
|---|---|---|
| **Clientes simultáneos** | 1 | Múltiples |
| **Puerto** | 5000 | 5001 |
| **Concurrencia** | No | Sí |
| **Thread-safe** | N/A | Sí (locks) |
| **Validación NRC** | No | Sí |
| **Escalabilidad** | Baja | Alta |

---

## Requisitos

- Python 3.6+
- Módulos: `socket`, `csv`, `json`, `os`, `threading` (estándar)

---

## Casos de Prueba

### Parte 1: Sin Hilos
1. Iniciar servidor sin hilos (puerto 5000)
2. Conectar 1 cliente → Realizar operaciones CRUD
3. Intentar conectar 2º cliente → Quedará en espera hasta que el primero se desconecte

### Parte 2: Con Hilos + Validación NRC

#### Prueba 1: NRC Válido
1. Iniciar servidor de NRCs (puerto 12346)
2. Iniciar servidor de calificaciones (puerto 5001)
3. Conectar cliente y agregar calificación con NRC válido (ej. MAT101)
4. **Resultado esperado:** ✓ "Calificación agregada correctamente (NRC: MAT101 - Matemáticas I)"

#### Prueba 2: NRC Inválido
1. Con ambos servidores activos
2. Intentar agregar calificación con NRC inválido (ej. ABC999)
3. **Resultado esperado:** ✗ "NRC no válido: NRC no existe en la base de datos"

#### Prueba 3: Concurrencia
1. Conectar 3-5 clientes simultáneamente
2. Cliente A: Agregar con MAT101
3. Cliente B: Agregar con FIS101
4. Cliente C: Listar calificaciones
5. **Resultado esperado:** Todos los clientes operan sin interferencia

#### Prueba 4: Servidor NRC Caído
1. Detener servidor de NRCs (Ctrl+C)
2. Intentar agregar calificación desde cliente
3. **Resultado esperado:** ✗ "Error: Servidor de NRCs no disponible"

#### Prueba 5: Actualizar con Cambio de NRC
1. Actualizar calificación existente
2. Seleccionar cambiar NRC
3. Ingresar nuevo NRC válido (ej. PRG101)
4. **Resultado esperado:** ✓ "Calificación actualizada correctamente (Nuevo NRC: PRG101 - Programación I)"

---

**Laboratorio 2 - Aplicaciones Distribuidas**
