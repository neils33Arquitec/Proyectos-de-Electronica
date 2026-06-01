# Especificaciones Técnicas del Sistema — v2

## Microcontroladores

### Arduino Uno (Controlador Principal)
| Parámetro         | Valor                    |
|-------------------|--------------------------|
| Microcontrolador  | ATmega328P               |
| Frecuencia CPU    | 16 MHz                   |
| RAM               | 2 KB SRAM                |
| Flash             | 32 KB                    |
| Voltaje lógico    | 5 V                      |
| GPIOs usados      | 2, 6, 7, 8, 9, 10, 11   |
| Serial de debug   | USB (pines 0/1) @ 115200 |

### ESP32 (Interfaz WiFi)
| Parámetro         | Valor                    |
|-------------------|--------------------------|
| Microcontrolador  | Xtensa LX6 (doble núcleo)|
| Frecuencia CPU    | 240 MHz                  |
| RAM               | 520 KB SRAM              |
| Flash             | 4 MB                     |
| Voltaje lógico    | 3.3 V                    |
| GPIOs usados      | 16 (RX), 17 (TX)         |
| WiFi              | 802.11 b/g/n 2.4 GHz, modo AP|
| IP del AP         | 192.168.4.1              |

---

## Sensores

### Caudalímetro GFS401
| Parámetro              | Valor                      |
|------------------------|----------------------------|
| Voltaje de operación   | 5 VDC                      |
| Rango de caudal        | 1 – 30 L/min               |
| Salida                 | Pulsos digitales TTL       |
| Factor de calibración  | 7.5 pulsos / (L/min)       |
| Conexión señal         | Arduino pin 2 (INT0, INPUT_PULLUP) |

### Sensor Ultrasónico HC-SR04 (Nivel)
| Parámetro              | Valor                      |
|------------------------|----------------------------|
| Voltaje de operación   | 5 VDC                      |
| Rango de medición      | 2 – 400 cm                 |
| Resolución             | 0.3 cm                     |
| Salida                 | Pulso PWM (ancho proporcional a distancia) |
| Ángulo de apertura     | 15°                        |
| Conexión               | TRIG→pin 9, ECHO→pin 8     |
| Fórmula de distancia   | d = (t_echo × 0.0343) / 2  [cm] |
| Nivel (%)              | ((MAX_DIST - d) / MAX_DIST) × 100 |

---

## Actuadores

### Bombas de Agua DC
| Parámetro              | Valor                      |
|------------------------|----------------------------|
| Voltaje operación      | 5 V ó 12 V (verificar modelo)|
| Control                | Relé de 2 canales (activo LOW)|
| Bomba 1 (Llenado)      | Arduino pin 6 → Relé IN1   |
| Bomba 2 (Descarga)     | Arduino pin 7 → Relé IN2   |

---

## Interfaz de Comunicación

### Serial Arduino Uno → ESP32
| Parámetro       | Valor              |
|-----------------|--------------------|
| Protocolo       | UART asíncrono     |
| Velocidad       | 9600 baud, 8N1     |
| Arduino TX      | Pin 11 (SoftwareSerial) → divisor de tensión |
| Arduino RX      | Pin 10 (SoftwareSerial) ← ESP32 TX            |
| ESP32 RX        | GPIO 16 (Serial2)  |
| ESP32 TX        | GPIO 17 (Serial2)  |
| Periodo envío   | 1 s                |

### Divisor de Tensión (5V → 3.3V)
```
Arduino TX (5V) ──┬── R1=10kΩ ──── ESP32 RX (3.3V)
                  │
                  R2=20kΩ
                  │
                 GND
```
V_out = 5V × 20k/(10k+20k) = **3.33 V** ✓

---

## Parámetros de Control

| Parámetro            | Valor por defecto | Rango ajustable |
|----------------------|-------------------|-----------------|
| Setpoint de nivel    | 80 %              | 0 – 100 %       |
| Banda de histéresis  | ±5 %              | Configurable    |
| Periodo de muestreo  | 1 s               | —               |
| Caudal mínimo alarma | 0.5 L/min         | Configurable    |

---

## Requisitos de Alimentación

| Componente         | Corriente estimada |
|--------------------|--------------------|
| Arduino Uno        | ~50 mA             |
| ESP32              | ~240 mA (WiFi activo)|
| HC-SR04            | ~15 mA             |
| GFS401             | ~15 mA             |
| Lógica relés       | ~20 mA             |
| Bombas             | 500 mA – 2 A c/u (verificar)|

Usar fuente separada para bombas. Compartir GND con Arduino.
