#pragma once

// ─── UART2 — comunicación con Arduino Uno ─────────────────────────────────────
// Arduino TX → divisor 5V→3.3V → ESP32 GPIO 16
// ESP32 GPIO 17 → Arduino RX (3.3V compatible con 5V TTL)
#define UART2_RX_PIN    16
#define UART2_TX_PIN    17
#define UART2_BAUD    9600

// ─── Punto de acceso WiFi ─────────────────────────────────────────────────────
#define WIFI_SSID   "ESP32-Llenado"
#define WIFI_PASS   "control2026"
// Dirección IP por defecto del AP: 192.168.4.1

// ─── Servidor web ─────────────────────────────────────────────────────────────
#define WEB_PORT  80

// ─── Tiempo máximo sin datos del Arduino antes de marcar "sin conexión" ────────
#define TIMEOUT_ARDUINO_MS  5000
