# Lista de Materiales — Sistema de Llenado de Flujo Continuo

**Proyecto:** Sistema de Llenado con ESP32, Arduino Uno y Sensor de Nivel  
**Universidad Santiago Mariño — Teoría Moderna de Control**  
**Versión:** 2.0 | Fecha: Junio 2026

---

## 1. Microcontroladores y Módulos Electrónicos

| # | Componente               | Modelo / Referencia     | Cant. | Descripción                                          |
|---|--------------------------|-------------------------|-------|------------------------------------------------------|
| 1 | Microcontrolador         | Arduino Uno R3          | 1     | Controlador principal; ATmega328P, 5V, 16 MHz        |
| 2 | Módulo WiFi              | ESP32 DevKit V1         | 1     | Interfaz WiFi; Xtensa LX6, 3.3V, 240 MHz            |
| 3 | Módulo relé              | Relé 2 canales 5V       | 1     | Control de bombas; activo LOW, optoacoplado          |

---

## 2. Sensores

| # | Componente               | Modelo / Referencia     | Cant. | Descripción                                          |
|---|--------------------------|-------------------------|-------|------------------------------------------------------|
| 4 | Sensor ultrasónico       | HC-SR04                 | 1     | Medición de nivel; rango 2–400 cm, 5V                |
| 5 | Caudalímetro             | GFS401                  | 1     | Medición de caudal; 1–30 L/min, salida de pulsos 5V  |

---

## 3. Actuadores

| # | Componente               | Modelo / Referencia     | Cant. | Descripción                                          |
|---|--------------------------|-------------------------|-------|------------------------------------------------------|
| 6 | Bomba de agua DC         | Mini bomba 5V ó 12V DC  | 2     | Bomba 1: llenado. Bomba 2: descarga/recirculación    |

> Verificar el voltaje exacto del modelo adquirido (5V o 12V). Elegir la fuente de alimentación acorde.

---

## 4. Alimentación

| # | Componente               | Modelo / Referencia         | Cant. | Descripción                                      |
|---|--------------------------|-----------------------------|-------|--------------------------------------------------|
| 7 | Fuente de alimentación   | 5V / 2A (USB o regulada)    | 1     | Para Arduino Uno, ESP32, sensores y lógica relé  |
| 8 | Fuente para bombas       | 5V/2A ó 12V/2A (según bomba)| 1     | Alimentación independiente para ambas bombas     |
| 9 | Cable USB tipo B         | Estándar                    | 1     | Programación y alimentación del Arduino Uno      |
|10 | Cable USB micro o tipo C | Según modelo ESP32          | 1     | Programación y alimentación del ESP32            |

> **Nota de seguridad:** No alimentar las bombas desde el mismo regulador que los microcontroladores. Las bombas generan picos de corriente que pueden reiniciar la placa.

---

## 5. Componentes Pasivos

| # | Componente    | Valor     | Cant. | Descripción                                              |
|---|---------------|-----------|-------|----------------------------------------------------------|
|11 | Resistencia   | 10 kΩ     | 2     | Divisor de tensión: R1 (Arduino TX → ESP32 RX)           |
|12 | Resistencia   | 20 kΩ     | 2     | Divisor de tensión: R2 (o usar 2× 10 kΩ en serie)       |

### Divisor de tensión necesario
El Arduino Uno opera a 5V lógicos; el ESP32 acepta máximo 3.6V en sus entradas.  
La señal TX del Arduino **debe** dividirse antes de conectarse al RX del ESP32.

```
Arduino TX ─── R1 (10kΩ) ───┬─── ESP32 RX
                             │
                           R2 (20kΩ)
                             │
                            GND

V_salida = 5V × 20k/(10k+20k) = 3.33 V  ✓
```

---

## 6. Cableado y Conexiones

| # | Componente            | Cant.  | Descripción                                             |
|---|-----------------------|--------|---------------------------------------------------------|
|13 | Cables Dupont M-M     | 30 uds | Conexiones entre módulos en protoboard                  |
|14 | Cables Dupont M-H     | 20 uds | Conexiones sensor HC-SR04 y módulos con pines hembra    |
|15 | Protoboard            | 1      | 830 puntos mínimo; para divisor de tensión y prototipado|
|16 | Manguera flexible     | 2 m    | Diámetro interior 6–8 mm; compatible con la bomba       |
|17 | Abrazaderas de manguera| 4 uds | Para asegurar mangueras a las bombas y caudalímetro     |

---

## 7. Estructural / Contenedor

| # | Componente            | Cant.  | Descripción                                             |
|---|-----------------------|--------|---------------------------------------------------------|
|18 | Depósito principal    | 1      | Tanque plástico 5–10 L; con tapa para montar HC-SR04    |
|19 | Depósito secundario   | 1      | Reservorio de agua para las bombas (opcional)           |
|20 | Cinta aislante        | 1 rollo| Aislamiento de empalmes y protección de cables          |
|21 | Termocontraíble       | 1 pack | Para empalmes de cables de bombas                       |
|22 | Soporte / caja        | 1      | Caja de proyecto o tablero acrílico para fijar placas   |

---

## 8. Herramientas (no se adquieren, se usan en laboratorio)

| Herramienta             | Uso                                              |
|-------------------------|--------------------------------------------------|
| Computadora con Arduino IDE 2.x | Carga del firmware a Arduino y ESP32   |
| Multímetro              | Verificación de voltajes y continuidad           |
| Cautín y estaño         | Soldadura de cables de bombas (si es necesario)  |
| Alicates / pelacables   | Preparación de cables                            |
| Regla / cinta métrica   | Medición para posicionamiento del HC-SR04        |

---

## 9. Software Requerido (gratuito)

| Software           | Versión    | Uso                                              | Descarga                  |
|--------------------|------------|--------------------------------------------------|---------------------------|
| Arduino IDE        | 2.x        | Compilación y carga de firmware                  | arduino.cc/en/software    |
| Soporte ESP32      | Espressif  | Agregar placas ESP32 al Arduino IDE              | Via gestor de placas       |
| MATLAB             | R2023+     | Simulación y modelado matemático                 | mathworks.com             |

### Instalación del soporte ESP32 en Arduino IDE
1. Archivo → Preferencias → URLs adicionales:  
   `https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json`
2. Herramientas → Gestor de tarjetas → buscar "esp32" → Instalar (Espressif Systems)
3. Seleccionar placa: **ESP32 Dev Module**

---

## 10. Resumen de Costos Estimados

| Categoría             | Ítems    | Costo estimado (USD) |
|-----------------------|----------|----------------------|
| Microcontroladores    | 1+2      | $12 – $18            |
| Sensores              | 4+5      | $8 – $15             |
| Actuadores            | 6        | $6 – $12             |
| Alimentación          | 7+8+9+10 | $8 – $15             |
| Componentes pasivos   | 11+12    | $1 – $2              |
| Cableado y estructura | 13–22    | $10 – $20            |
| **TOTAL ESTIMADO**    |          | **$45 – $82 USD**    |

> Los precios varían según proveedor local. Verificar disponibilidad en tiendas de electrónica o plataformas de importación.
