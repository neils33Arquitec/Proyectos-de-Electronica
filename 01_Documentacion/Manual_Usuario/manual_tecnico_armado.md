# Manual Técnico de Armado y Descripción
## Sistema de Llenado de Flujo Continuo con Arduino Uno, ESP32 y Sensor HC-SR04

**Universidad Santiago Mariño — Teoría Moderna de Control**  
**Versión:** 2.0 | Fecha: Junio 2026  
**Dirigido a:** Técnicos y estudiantes con conocimiento básico de electrónica

---

## Descripción General del Sistema

El sistema controla automáticamente el llenado de un tanque de agua midiendo dos variables físicas:

| Variable    | Sensor    | Microcontrolador que la lee |
|-------------|-----------|----------------------------|
| Nivel (%)   | HC-SR04   | Arduino Uno (pin 8/9)       |
| Caudal (L/min) | GFS401 | Arduino Uno (pin 2, INT0)  |

El **Arduino Uno** actúa como **controlador**: lee los sensores, ejecuta el algoritmo de histéresis y acciona las bombas mediante un módulo relé.

El **ESP32** actúa como **interfaz de usuario**: recibe datos del Arduino por comunicación serial, crea una red WiFi propia y sirve una aplicación web accesible desde cualquier teléfono o computadora.

```
┌──────────────────────────────────────────────────────────────────┐
│                        ARDUINO UNO                               │
│                                                                  │
│  ┌─────────┐   nivel %   ┌──────────────────────┐               │
│  │ HC-SR04 ├────────────►│                      ├──Pin 6──► RLÉ1 ──► BOMBA 1
│  └─────────┘             │  Algoritmo de        │               │
│  ┌─────────┐  caudal     │  Control             │               │
│  │ GFS401  ├────────────►│  (Histéresis)        ├──Pin 7──► RLÉ2 ──► BOMBA 2
│  └─────────┘             └──────────────────────┘               │
│                                    │                             │
│                             SoftwareSerial                       │
│                              Pin 10/11                           │
└────────────────────────────────────┬─────────────────────────────┘
                                     │  UART 9600 baud
                                     │  (divisor 5V→3.3V en TX)
┌────────────────────────────────────▼─────────────────────────────┐
│                           ESP32                                  │
│                                                                  │
│   Serial2 (GPIO 16/17) ──► Parseo de estado                     │
│   WiFi AP "ESP32-Llenado" ──► Servidor web en 192.168.4.1       │
└──────────────────────────────────────────────────────────────────┘
```

---

## Herramientas Necesarias

- Computadora con Arduino IDE 2.x instalado y soporte de placas ESP32
- Multímetro digital
- Cautín y estaño (para terminales de bombas)
- Pelacables y alicates
- Regla o cinta métrica
- Cinta aislante o termocontraíble

---

## Paso 1 — Verificación de Componentes

Antes de comenzar el armado, verificar la presencia y funcionamiento de cada componente:

| Componente          | Verificación                                                    |
|---------------------|-----------------------------------------------------------------|
| Arduino Uno         | Conectar por USB; el LED L (pin 13) debe parpadear (Blink)     |
| ESP32               | Conectar por USB; visible en el administrador de dispositivos  |
| HC-SR04             | Medir VCC=5V y GND con el multímetro antes de conectarlo       |
| GFS401              | Soplar por el tubo; debe sonar el rodete girando               |
| Módulo relé         | Con 5V en VCC/GND y IN a GND, el relé debe activarse (clic)   |
| Bombas DC           | Conectar directamente a la fuente; deben bombear agua           |

---

## Paso 2 — Preparación del Sistema Hidráulico

### 2.1 Tanque principal
1. Seleccionar un recipiente plástico de **5 a 10 litros** con tapa rígida.
2. Marcar el centro de la tapa para hacer un orificio donde irá el HC-SR04.
3. Hacer un orificio de ~25 mm de diámetro en la tapa (solo si se coloca dentro).  
   Alternativa: fijar el HC-SR04 encima de la tapa apuntando hacia abajo.
4. El sensor debe quedar a **exactamente MAX_DIST_CM** (por defecto: 30 cm) del fondo del tanque cuando está vacío. Medir y ajustar el valor en `config_arduino.h`.

### 2.2 Instalación del caudalímetro GFS401
1. Colocar el GFS401 **en línea** con la manguera de salida de la Bomba 1 (entrada del tanque).
2. Respetar la dirección de flujo indicada con la flecha en el cuerpo del sensor.
3. Conectar abrazaderas en ambos extremos del sensor para evitar fugas.
4. El sensor debe instalarse en posición **horizontal o vertical con flujo hacia arriba** para lectura precisa.

```
  BOMBA 1 ──[manguera]──► GFS401 ──[manguera]──► TANQUE (entrada)
                           ↑ dirección flujo →
```

### 2.3 Conexión de mangueras
| Tramo                    | Descripción                                       |
|--------------------------|---------------------------------------------------|
| Reservorio → Bomba 1     | Manguera de admisión de la bomba de llenado       |
| Bomba 1 → GFS401 → Tanque| Manguera de descarga con el caudalímetro en línea |
| Tanque → Bomba 2         | Manguera de admisión de la bomba de descarga      |
| Bomba 2 → Reservorio     | Manguera de retorno (circuito cerrado)            |

---

## Paso 3 — Cableado del Módulo Relé

El módulo de 2 canales tiene la siguiente distribución de pines:

```
┌─────────────────────────────────────┐
│  VCC  GND  IN1  IN2                 │  ← Lado de control (lógica 5V)
│                                     │
│  COM1 NO1 NC1  COM2 NO2 NC2         │  ← Lado de potencia (bombas)
└─────────────────────────────────────┘
```

| Pin relé | Conexión          | Descripción                        |
|----------|-------------------|------------------------------------|
| VCC      | Arduino 5V        | Alimentación del módulo            |
| GND      | Arduino GND       | Tierra común                       |
| IN1      | Arduino pin 6     | Control bomba 1 (activo LOW)       |
| IN2      | Arduino pin 7     | Control bomba 2 (activo LOW)       |
| COM1     | + fuente bombas   | Terminal común bomba 1             |
| NO1      | + Bomba 1         | Normalmente abierto (bomba apagada)|
| COM2     | + fuente bombas   | Terminal común bomba 2             |
| NO2      | + Bomba 2         | Normalmente abierto (bomba apagada)|

> **Importante:** Conectar el **GND de la fuente de bombas** también al GND del Arduino para establecer tierra común entre ambas fuentes.

---

## Paso 4 — Cableado del HC-SR04 al Arduino

| Pin HC-SR04 | Conexión Arduino Uno |
|-------------|----------------------|
| VCC         | 5V                   |
| GND         | GND                  |
| TRIG        | Pin 9 (salida)       |
| ECHO        | Pin 8 (entrada)      |

> El HC-SR04 opera a 5V. La señal ECHO que devuelve también es de 5V, lo cual es compatible directamente con el Arduino Uno (no requiere divisor).

---

## Paso 5 — Cableado del GFS401 al Arduino

| Pin GFS401  | Conexión Arduino Uno |
|-------------|----------------------|
| VCC (rojo)  | 5V                   |
| GND (negro) | GND                  |
| Señal (amarillo) | Pin 2 (INT0, INPUT_PULLUP) |

> El pin 2 es el único que soporta la interrupción INT0 en el Arduino Uno. **No cambiar a otro pin** sin modificar el firmware.

---

## Paso 6 — Construcción del Divisor de Tensión (5V → 3.3V)

Este circuito es **obligatorio** para proteger el ESP32. El TX del Arduino emite 5V; el RX del ESP32 acepta máximo 3.6V.

### Materiales: 1× resistencia 10 kΩ, 1× resistencia 20 kΩ

```
                        ┌── ESP32 GPIO 16 (RX)
Arduino pin 11 (TX) ───[10kΩ]───┤
                                └───[20kΩ]─── GND
```

### Cálculo de verificación:
```
V_out = V_in × R2/(R1+R2) = 5V × 20000/(10000+20000) = 3.33 V  ✓
```

### Construcción en protoboard:
```
Fila A: [Arduino pin 11] ── [pata 1 de R1(10kΩ)]
Fila B: [pata 2 de R1(10kΩ)] ── [pata 1 de R2(20kΩ)] ── [ESP32 GPIO 16]
Fila C: [pata 2 de R2(20kΩ)] ── [GND]
```

---

## Paso 7 — Conexiones Completas del Arduino Uno

Resumen de todos los cables que llegan al Arduino Uno:

| Pin Arduino | Señal                  | Destino                            |
|-------------|------------------------|------------------------------------|
| 5V          | Alimentación 5V        | VCC: HC-SR04, GFS401, Relé         |
| GND         | Tierra común           | GND: HC-SR04, GFS401, Relé, ESP32  |
| Pin 2       | GFS401 señal           | GFS401 señal (amarillo)            |
| Pin 6       | Relé IN1               | Control Bomba 1                    |
| Pin 7       | Relé IN2               | Control Bomba 2                    |
| Pin 8       | HC-SR04 ECHO (entrada) | HC-SR04 ECHO                       |
| Pin 9       | HC-SR04 TRIG (salida)  | HC-SR04 TRIG                       |
| Pin 10      | SS RX                  | ESP32 GPIO 17 (TX) — directo       |
| Pin 11      | SS TX                  | Divisor de tensión → ESP32 GPIO 16 |

---

## Paso 8 — Conexiones del ESP32

| Pin ESP32   | Señal              | Destino                                   |
|-------------|--------------------|-------------------------------------------|
| 3.3V        | Alimentación       | (puede alimentarse por USB independiente) |
| GND         | Tierra común       | GND del Arduino                           |
| GPIO 16 (RX2) | UART2 RX         | Salida del divisor de tensión             |
| GPIO 17 (TX2) | UART2 TX         | Arduino pin 10 (SoftwareSerial RX) directo|

> El ESP32 se puede alimentar por su propio cable USB mientras el Arduino se alimenta por el suyo. Compartir **solo el GND**.

---

## Paso 9 — Diagrama de Conexiones General (ASCII)

```
+5V ──────────┬──── VCC HC-SR04
              ├──── VCC GFS401
              └──── VCC Módulo Relé

GND ──────────┬──── GND HC-SR04
              ├──── GND GFS401
              ├──── GND Módulo Relé
              ├──── GND ESP32
              └──── GND Fuente Bombas

ARDUINO UNO
  Pin 2 ──── GFS401 Señal (amarillo)
  Pin 6 ──── Módulo Relé IN1
  Pin 7 ──── Módulo Relé IN2
  Pin 8 ──── HC-SR04 ECHO
  Pin 9 ──── HC-SR04 TRIG
  Pin 10──── ESP32 GPIO 17 (TX2)  [directo, 3.3V compatible]
  Pin 11──── R1 10kΩ ──┬── ESP32 GPIO 16 (RX2)
                       └── R2 20kΩ ── GND

MÓDULO RELÉ
  NO1 ──── +Bomba 1 ──── Fuente bombas COM1
  NO2 ──── +Bomba 2 ──── Fuente bombas COM2
  GND bombas ──── GND Arduino

ESP32
  GPIO 16 (RX2) ──── [divisor de tensión] ──── Arduino pin 11
  GPIO 17 (TX2) ──── Arduino pin 10
  GND ──── GND Arduino
```

---

## Paso 10 — Carga del Firmware en el Arduino Uno

1. Abrir Arduino IDE 2.x.
2. Ir a **Archivo → Abrir** y navegar a:  
   `04_Firmware/arduino_uno/controlador_principal/controlador_principal.ino`
3. Seleccionar la placa: **Herramientas → Placa → Arduino Uno**
4. Seleccionar el puerto COM: **Herramientas → Puerto → COMx (Arduino Uno)**
5. Verificar que `config_arduino.h` está en la carpeta `../include/` relativa al `.ino`.  
   Si Arduino IDE no lo encuentra, copiar el contenido de `config_arduino.h` al inicio del `.ino`.
6. Hacer clic en **Cargar (→)**.
7. Verificar en el Monitor Serie (115200 baud) el mensaje:  
   `Controlador principal iniciado.`

### Ajuste de MAX_DIST_CM (obligatorio)
En `config_arduino.h`, cambiar el valor de `MAX_DIST_CM` a la distancia real (en cm) medida desde el sensor HC-SR04 hasta el fondo del tanque vacío:
```cpp
#define MAX_DIST_CM  30.0f   // ← cambiar por tu medición real
```

---

## Paso 11 — Carga del Firmware en el ESP32

1. En Arduino IDE, ir a **Herramientas → Placa → ESP32 Arduino → ESP32 Dev Module**
2. Seleccionar el puerto COM del ESP32.
3. Configurar:
   - Upload Speed: `115200`
   - Flash Size: `4MB`
4. Abrir: `04_Firmware/esp32/interfaz_wifi/interfaz_wifi.ino`
5. Verificar credenciales WiFi en `config_esp32.h`:
   ```cpp
   #define WIFI_SSID   "ESP32-Llenado"
   #define WIFI_PASS   "control2026"
   ```
6. Hacer clic en **Cargar (→)**. Si falla, mantener presionado el botón BOOT del ESP32 durante la carga.
7. Verificar en Monitor Serie (115200 baud):
   ```
   AP: ESP32-Llenado  IP: 192.168.4.1
   Servidor web listo.
   ```

---

## Paso 12 — Prueba Inicial del Sistema

### Prueba 1: Verificación del sensor HC-SR04
1. Con el sistema encendido, abrir el Monitor Serie del Arduino a 115200 baud.
2. Colocar un objeto a distintas distancias del sensor.
3. Verificar que el nivel (%) cambia de forma coherente.
4. Si el nivel muestra 0% con el tanque lleno, verificar que `MAX_DIST_CM` está bien configurado.

### Prueba 2: Verificación del caudalímetro
1. Activar la Bomba 1 desde la app web (modo MANUAL, botón ON Bomba 1).
2. Verificar que el Monitor Serie muestra un caudal > 0.5 L/min mientras el agua circula.
3. Si el caudal es siempre 0, verificar la conexión del cable amarillo al pin 2 del Arduino.

### Prueba 3: Verificación de la app WiFi
1. Buscar en el teléfono la red WiFi **ESP32-Llenado**.
2. Conectar con contraseña **control2026**.
3. Abrir el navegador y escribir: **192.168.4.1**
4. La aplicación de control debe cargarse en menos de 3 segundos.
5. Los datos de nivel y caudal deben actualizarse cada 1 segundo.

### Prueba 4: Verificación del modo AUTO
1. Desde la app web, poner modo **AUTO** y setpoint al **80%**.
2. Con el tanque vacío, la Bomba 1 debe encenderse automáticamente.
3. Al alcanzar el 85% (80% + 5% histéresis), la Bomba 1 debe apagarse.
4. Al bajar del 75%, debe volver a encenderse.

---

## Resolución de Problemas Comunes

| Síntoma                          | Causa probable                            | Solución                                            |
|----------------------------------|-------------------------------------------|-----------------------------------------------------|
| App web no carga                 | No conectado al WiFi del ESP32            | Verificar conexión a "ESP32-Llenado"                |
| Nivel siempre en 0% o 100%       | MAX_DIST_CM incorrecto                    | Medir distancia real y actualizar config_arduino.h  |
| Caudal siempre 0                 | GFS401 no conectado al pin 2              | Verificar cable señal; revisar soldaduras           |
| Bombas no responden              | Relé no activado / cables cruzados        | Verificar IN1/IN2; el relé activo LOW activa con GND|
| ESP32 no arranca tras carga      | Código no compiló correctamente           | Revisar mensajes de error en Arduino IDE            |
| Arduino reinicia al activar bomba| Pico de corriente de la bomba             | Usar fuente independiente para las bombas           |
| App muestra "Sin conexión"       | Arduino no envía datos                    | Verificar conexión serial pin 10/11 y divisor tensión|
| Nivel oscila mucho               | Histéresis muy pequeña o sensor inestable | Aumentar HISTERESIS_PCT en config_arduino.h         |

---

## Parámetros Ajustables (config_arduino.h)

| Parámetro           | Por defecto | Efecto al aumentar                        |
|---------------------|-------------|-------------------------------------------|
| `MAX_DIST_CM`        | 30.0        | Cambia la escala del nivel medido         |
| `LECTURAS_PROMEDIO`  | 3           | Mayor estabilidad, menor velocidad        |
| `HISTERESIS_PCT`     | 5           | Menos ciclos ON/OFF, mayor error estático |
| `SETPOINT_DEFAULT`   | 80          | Nivel objetivo inicial al encender        |
| `CAUDAL_MIN_ALARMA`  | 0.5 L/min   | Umbral para activar alarma                |
| `T_CONTROL_MS`       | 200 ms      | Frecuencia de lectura del HC-SR04         |
| `T_ENVIO_MS`         | 1000 ms     | Frecuencia de envío de datos al ESP32     |
