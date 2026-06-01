#pragma once

// ─── Pines Arduino Uno ────────────────────────────────────────────────────────
#define GFS401_PIN    2    // INT0 — caudalímetro (FALLING)
#define ECHO_PIN      8    // HC-SR04 echo
#define TRIG_PIN      9    // HC-SR04 trigger
#define BOMBA1_PIN    6    // Relé bomba 1 (activo LOW)
#define BOMBA2_PIN    7    // Relé bomba 2 (activo LOW)
#define SS_RX_PIN    10    // SoftwareSerial RX ← ESP32 TX
#define SS_TX_PIN    11    // SoftwareSerial TX → ESP32 RX (divisor de tensión 5V→3.3V)

// ─── Calibración GFS401 ───────────────────────────────────────────────────────
#define FACTOR_CAL_GFS401   7.5f    // pulsos / (L/min)

// ─── Tanque — ajustar con medición real ───────────────────────────────────────
// HC-SR04 montado en la tapa; MAX_DIST_CM = distancia al fondo con tanque vacío
#define MAX_DIST_CM        30.0f    // [cm]
#define LECTURAS_PROMEDIO   3       // promediar N mediciones del ultrasónico

// ─── Control por histéresis ───────────────────────────────────────────────────
#define HISTERESIS_PCT      5       // ±5 % alrededor del setpoint
#define SETPOINT_DEFAULT   80       // % de nivel inicial

// ─── Temporizadores ──────────────────────────────────────────────────────────
#define T_CONTROL_MS      200       // período de lectura del ultrasónico [ms]
#define T_ENVIO_MS       1000       // período de envío de estado al ESP32 [ms]

// ─── Alarma: sin caudal con bomba encendida ───────────────────────────────────
#define CAUDAL_MIN_ALARMA  0.5f     // L/min — por debajo → posible falla
