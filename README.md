# Sistema de Llenado de Flujo Continuo — v2

**Universidad Santiago Mariño**  
**Asignatura:** Teoría Moderna de Control  
**Autor:** Neil Edickson Suarez Arevalo (NeilsAraquitec)  
**Co-Autor:** Jose Fabian Salas Garcia  
**Última actualización:** Sesión 002 — Junio 2026

---

## Descripción General

Sistema automático de llenado con **dos variables de control** (nivel y caudal),  
implementado sobre una arquitectura de dos microcontroladores:

- **Arduino Uno** — Controlador principal: lee sensores, ejecuta algoritmo de control, maneja relés.
- **ESP32** — Interfaz WiFi: recibe datos del Arduino, sirve una app web de monitoreo y control remoto.

---

## Arquitectura del Sistema

```
  ┌─────────────────────────────────────────────────────┐
  │                    ARDUINO UNO                       │
  │                                                      │
  │  HC-SR04 ──► nivel (%)      ┌─────────────┐         │
  │  GFS401  ──► caudal(L/min)  │  Control    │──► Relé ──► Bomba 1 (Llenado)
  │                             │  Histéresis │──► Relé ──► Bomba 2 (Descarga)
  │                             └─────────────┘         │
  │                          SoftwareSerial (9600)       │
  └──────────────────────────┬──────────────────────────┘
                             │ TX→RX / RX←TX (divisor 5V→3.3V en TX)
  ┌──────────────────────────▼──────────────────────────┐
  │                      ESP32                           │
  │                                                      │
  │   Serial2 (GPIO 16/17) ──► Parseo de estado         │
  │   WiFi AP "ESP32-Llenado" ──► 192.168.4.1           │
  │   Servidor Web ──► App HTML/JS embebida              │
  └──────────────────────────┬──────────────────────────┘
                             │ WiFi 2.4 GHz
                    ┌────────▼────────┐
                    │  App Web        │
                    │  (navegador     │
                    │   del celular)  │
                    └─────────────────┘
```

---

## Hardware

| Componente              | Cant | Conexión al Arduino Uno          | Notas                         |
|-------------------------|------|----------------------------------|-------------------------------|
| Arduino Uno             | 1    | —                                | Controlador principal         |
| ESP32                   | 1    | Pines 10/11 (SoftwareSerial)     | Interfaz WiFi                 |
| HC-SR04 (nivel)         | 1    | TRIG→9, ECHO→8                   | Montado en tapa del tanque    |
| Caudalímetro GFS401     | 1    | Señal→2 (INT0)                   | 7.5 pulsos/(L/min)            |
| Bomba DC (llenado)      | 1    | Relé→6                           | 5V ó 12V según modelo         |
| Bomba DC (descarga)     | 1    | Relé→7                           | 5V ó 12V según modelo         |
| Módulo relé 2 canales   | 1    | IN1→6, IN2→7                     | Activo LOW                    |
| Fuente de alimentación  | 1    | —                                | 5V/12V según bombas           |

### Pines Arduino Uno — resumen

| Pin   | Función                               |
|-------|---------------------------------------|
| 2     | GFS401 señal (INT0, FALLING)          |
| 8     | HC-SR04 ECHO                          |
| 9     | HC-SR04 TRIG                          |
| 6     | Relé Bomba 1                          |
| 7     | Relé Bomba 2                          |
| 10    | SoftwareSerial RX ← ESP32 TX          |
| 11    | SoftwareSerial TX → ESP32 RX (div.)   |

### Pines ESP32

| Pin     | Función                               |
|---------|---------------------------------------|
| GPIO 16 | UART2 RX ← Arduino TX (div. tensión)  |
| GPIO 17 | UART2 TX → Arduino RX                 |

> **Divisor de tensión (5V → 3.3V):** R1=10kΩ, R2=20kΩ en el TX del Arduino hacia el RX del ESP32.

---

## Protocolo de Comunicación Serial

**9600 baud, 8N1.**

```
Arduino → ESP32 (cada 1 s):
   N:75.3,Q:2.15,B1:1,B2:0,SP:80,M:1,A:0

ESP32 → Arduino (comandos):
   B1:1   →  Bomba 1 ON         B1:0   →  Bomba 1 OFF
   B2:1   →  Bomba 2 ON         B2:0   →  Bomba 2 OFF
   SP:80  →  Setpoint = 80%     M:1    →  Modo AUTO
```

---

## Aplicación Web de Control

Conectar al WiFi **`ESP32-Llenado`** (contraseña: `control2026`)  
y abrir un navegador en **`192.168.4.1`**

**Funciones de la app:**
- Visualización de nivel en tiempo real (barra animada + setpoint naranja)
- Lectura de caudal (L/min)
- Estado de bombas (indicador verde/gris)
- Control manual de bombas (ON/OFF)
- Ajuste de setpoint de nivel (slider 0-100%)
- Toggle modo AUTO / MANUAL
- Alarma visual si bomba activa sin caudal detectado

---

## Estructura de Archivos

```
Proyecto segundo/
├── README.md                              ← este archivo
├── 01_Documentacion/
│   ├── Informe_Final/
│   ├── Especificaciones_Tecnicas/
│   ├── Manual_Usuario/
│   └── Presentacion/
├── 02_Modelado_Matematico/
│   ├── Funcion_de_Transferencia/          ← G(s) bomba + tanque, diseño PID
│   ├── Espacio_de_Estados/                ← Matrices A,B,C,D, LQR
│   └── Analisis_de_Estabilidad/
├── 03_Diseno_del_Sistema/
│   ├── Diagrama_de_Bloques/
│   ├── Diagrama_de_Flujo/
│   ├── Esquematicos/
│   └── PCB/
├── 04_Firmware/
│   ├── arduino_uno/
│   │   ├── controlador_principal/         ← controlador_principal.ino
│   │   └── include/config_arduino.h
│   ├── esp32/
│   │   ├── interfaz_wifi/                 ← interfaz_wifi.ino + app web embebida
│   │   └── include/config_esp32.h
│   └── src/                               ← v1 histórico (ESP32 standalone)
├── 05_Simulaciones/
│   ├── MATLAB_Simulink/                   ← simulacion_sistema_llenado.m (LQR)
│   └── Proteus/
├── 06_Resultados_y_Pruebas/
├── 07_Evidencias/
└── 08_Referencias/
```

---

## Entorno de Desarrollo

- **Arduino Uno firmware:** Arduino IDE 2.x — placa `Arduino Uno`
- **ESP32 firmware:** Arduino IDE 2.x — placa `ESP32 Dev Module`, librería WiFi incluida
- **Simulación:** MATLAB R2023+ con Control System Toolbox
