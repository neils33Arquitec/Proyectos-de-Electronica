/*
 * controlador_principal.ino
 * Arduino Uno — Controlador del sistema de llenado de flujo continuo
 * Universidad Santiago Mariño — Teoría Moderna de Control
 *
 * Responsabilidades:
 *   - Medir nivel con HC-SR04 (GPIO 8/9)
 *   - Medir caudal con GFS401 (INT0, GPIO 2)
 *   - Controlar 2 bombas DC via relés (GPIO 6/7)
 *   - Ejecutar control por histéresis (modo AUTO)
 *   - Comunicar estado al ESP32 vía SoftwareSerial (GPIO 10/11)
 *   - Recibir comandos del ESP32
 *
 * Protocolo serial (9600 baud):
 *   Arduino → ESP32:  N:xx.x,Q:x.xx,B1:x,B2:x,SP:xx,M:x,A:x\n
 *   ESP32 → Arduino:  B1:x / B2:x / SP:xx / M:x\n
 */

#include <SoftwareSerial.h>
#include "../include/config_arduino.h"

// ─── Hardware ────────────────────────────────────────────────────────────────
SoftwareSerial espSerial(SS_RX_PIN, SS_TX_PIN);

volatile uint16_t pulsos = 0;
void contarPulsos() { pulsos++; }   // ISR — INT0 FALLING

// ─── Estado del sistema ───────────────────────────────────────────────────────
struct Estado {
  float   nivel_pct   = 0.0f;
  float   caudal_lpm  = 0.0f;
  bool    bomba1      = false;
  bool    bomba2      = false;
  uint8_t setpoint    = SETPOINT_DEFAULT;
  bool    modo_auto   = true;
  bool    alarma      = false;   // bomba ON pero sin caudal
} est;

// ─── Temporizadores ──────────────────────────────────────────────────────────
unsigned long t_control = 0;
unsigned long t_envio   = 0;

// ─── Declaraciones ───────────────────────────────────────────────────────────
float   medirNivel();
float   medirCaudal();
void    ejecutarControl();
void    enviarEstado();
void    leerComandos();
void    setBomba(uint8_t n, bool on);

// =============================================================================
void setup() {
  Serial.begin(115200);
  espSerial.begin(9600);

  pinMode(TRIG_PIN,    OUTPUT);
  pinMode(ECHO_PIN,    INPUT);
  pinMode(BOMBA1_PIN,  OUTPUT);
  pinMode(BOMBA2_PIN,  OUTPUT);
  pinMode(GFS401_PIN,  INPUT_PULLUP);

  // Relés apagados al inicio (activo LOW → HIGH apaga)
  digitalWrite(BOMBA1_PIN, HIGH);
  digitalWrite(BOMBA2_PIN, HIGH);

  attachInterrupt(digitalPinToInterrupt(GFS401_PIN), contarPulsos, FALLING);

  Serial.println(F("Controlador principal iniciado."));
}

// =============================================================================
void loop() {
  unsigned long ahora = millis();

  // Lectura del nivel cada T_CONTROL_MS
  if (ahora - t_control >= T_CONTROL_MS) {
    t_control = ahora;
    est.nivel_pct = medirNivel();
  }

  // Caudal + control + envío cada T_ENVIO_MS
  if (ahora - t_envio >= T_ENVIO_MS) {
    t_envio = ahora;
    est.caudal_lpm = medirCaudal();

    // Detectar alarma: bomba 1 ON pero sin caudal detectable
    est.alarma = est.bomba1 && (est.caudal_lpm < CAUDAL_MIN_ALARMA);

    if (est.modo_auto) ejecutarControl();
    enviarEstado();
  }

  leerComandos();
}

// =============================================================================
// HC-SR04: promedia LECTURAS_PROMEDIO mediciones → nivel en %
float medirNivel() {
  float suma = 0;
  uint8_t validas = 0;

  for (uint8_t i = 0; i < LECTURAS_PROMEDIO; i++) {
    digitalWrite(TRIG_PIN, LOW);  delayMicroseconds(2);
    digitalWrite(TRIG_PIN, HIGH); delayMicroseconds(10);
    digitalWrite(TRIG_PIN, LOW);

    long dur = pulseIn(ECHO_PIN, HIGH, 30000UL);  // timeout 30 ms
    if (dur == 0) continue;

    float dist_cm = (dur * 0.0343f) / 2.0f;
    suma += dist_cm;
    validas++;
    delay(10);
  }

  if (validas == 0) return est.nivel_pct;   // mantener último valor

  float distancia = suma / validas;
  float nivel = ((MAX_DIST_CM - distancia) / MAX_DIST_CM) * 100.0f;
  return constrain(nivel, 0.0f, 100.0f);
}

// =============================================================================
// GFS401: cuenta pulsos acumulados en T_ENVIO_MS → L/min
float medirCaudal() {
  noInterrupts();
  uint16_t p = pulsos;
  pulsos = 0;
  interrupts();
  // Los pulsos se acumularon en exactamente T_ENVIO_MS = 1000 ms (1 s)
  return p / FACTOR_CAL_GFS401;
}

// =============================================================================
// Control por histéresis sobre nivel — solo mueve Bomba 1 (llenado)
void ejecutarControl() {
  float sp = (float)est.setpoint;

  if (est.nivel_pct < (sp - HISTERESIS_PCT)) {
    setBomba(1, true);
  } else if (est.nivel_pct > (sp + HISTERESIS_PCT)) {
    setBomba(1, false);
  }
  // Dentro de la banda de histéresis → no cambia estado (evita ciclos)
}

// =============================================================================
void setBomba(uint8_t n, bool on) {
  if (n == 1) {
    est.bomba1 = on;
    digitalWrite(BOMBA1_PIN, on ? LOW : HIGH);
  } else {
    est.bomba2 = on;
    digitalWrite(BOMBA2_PIN, on ? LOW : HIGH);
  }
}

// =============================================================================
// Protocolo: N:xx.x,Q:x.xx,B1:x,B2:x,SP:xx,M:x,A:x\n
void enviarEstado() {
  espSerial.print(F("N:"));  espSerial.print(est.nivel_pct, 1);
  espSerial.print(F(",Q:")); espSerial.print(est.caudal_lpm, 2);
  espSerial.print(F(",B1:")); espSerial.print(est.bomba1 ? 1 : 0);
  espSerial.print(F(",B2:")); espSerial.print(est.bomba2 ? 1 : 0);
  espSerial.print(F(",SP:")); espSerial.print(est.setpoint);
  espSerial.print(F(",M:"));  espSerial.print(est.modo_auto ? 1 : 0);
  espSerial.print(F(",A:"));  espSerial.println(est.alarma  ? 1 : 0);
}

// =============================================================================
// Recibe: B1:x | B2:x | SP:xx | M:x
void leerComandos() {
  if (!espSerial.available()) return;
  String cmd = espSerial.readStringUntil('\n');
  cmd.trim();
  if (cmd.length() < 3) return;

  if (cmd.startsWith(F("B1:"))) {
    est.modo_auto = false;
    setBomba(1, cmd.charAt(3) == '1');

  } else if (cmd.startsWith(F("B2:"))) {
    est.modo_auto = false;
    setBomba(2, cmd.charAt(3) == '1');

  } else if (cmd.startsWith(F("SP:"))) {
    est.setpoint = (uint8_t)constrain(cmd.substring(3).toInt(), 0, 100);

  } else if (cmd.startsWith(F("M:"))) {
    est.modo_auto = (cmd.charAt(2) == '1');
    // Al volver a AUTO, las bombas pasan al control de histéresis de inmediato
  }
}
