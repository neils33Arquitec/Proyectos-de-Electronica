/*
 * Sistema de Llenado de Flujo Continuo
 * Universidad Santiago Mariño - Teoria Moderna de Control
 *
 * Hardware:
 *   - ESP32
 *   - Caudalimetro GFS401  -> GPIO 4
 *   - Rele Bomba 1         -> GPIO 26
 *   - Rele Bomba 2         -> GPIO 27
 */

#include <Arduino.h>

#define SENSOR_FLUJO  4
#define BOMBA1       26
#define BOMBA2       27

// Factor de calibracion GFS401: 7.5 pulsos por litro/minuto
#define FACTOR_CALIBRACION 7.5f

volatile int pulsos = 0;

void IRAM_ATTR contarPulsos() {
  pulsos++;
}

void setup() {
  Serial.begin(115200);

  pinMode(BOMBA1, OUTPUT);
  pinMode(BOMBA2, OUTPUT);
  pinMode(SENSOR_FLUJO, INPUT_PULLUP);

  attachInterrupt(digitalPinToInterrupt(SENSOR_FLUJO), contarPulsos, FALLING);

  // Activar bombas (LOW = activo en modulos de rele tipicos)
  digitalWrite(BOMBA1, HIGH);
  digitalWrite(BOMBA2, HIGH);

  Serial.println("Sistema de llenado iniciado.");
}

void loop() {
  pulsos = 0;
  delay(1000);

  float caudal_lpm = pulsos / FACTOR_CALIBRACION;
  float volumen_ml  = (caudal_lpm / 60.0f) * 1000.0f;

  Serial.print("Caudal: ");
  Serial.print(caudal_lpm, 2);
  Serial.print(" L/min  |  Volumen aprox.: ");
  Serial.print(volumen_ml, 1);
  Serial.println(" mL/s");
}
