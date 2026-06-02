# PROTOCOLO DE ANÁLISIS Y AVANCE POR SESIONES

**Proyecto:** Sistema de Llenado de Flujo Continuo con Control Automático  
**Institución:** Universidad Santiago Mariño — Teoría Moderna de Control  
**Autor:** Neil Edickson Suarez Arevalo (NeilsAraquitec)  
**Co-Autor:** Jose Fabian Salas Garcia  
**Colaborador técnico:** Ingeniero Electrónico (IA de élite)  
**Repositorio:** https://github.com/neils33Arquitec/Proyectos-de-Electronica  
**Versión del protocolo:** 1.0 — Iniciado Sesión 001 (2026-06-01)

---

## PRINCIPIO DE TRABAJO

Cada sesión avanza **una o más áreas técnicas** con entregables concretos y verificables.  
Al iniciar: leer la bitácora de la sesión anterior en `SESIONES/`.  
Al cerrar: actualizar bitácora, hacer commit, push a GitHub.

---

## MAPA DE ÁREAS TÉCNICAS

```
ÁREA 1  ──► Identificación Experimental de Parámetros
ÁREA 2  ──► Modelado Matemático Completo
ÁREA 3  ──► Análisis de Estabilidad Formal
ÁREA 4  ──► Diagramas Técnicos (Bloques / Flujo / Esquemáticos)
ÁREA 5  ──► Mejoras de Firmware (Arduino + ESP32)
ÁREA 6  ──► Implementación del Controlador LQR en Firmware
ÁREA 7  ──► Validación Experimental y Registro de Datos
ÁREA 8  ──► Informe Final Académico
ÁREA 9  ──► Presentación (Diapositivas)
```

---

## ÁREA 1 — IDENTIFICACIÓN EXPERIMENTAL DE PARÁMETROS

**Estado:** ⬜ PENDIENTE  
**Prioridad:** ALTA — bloquea Áreas 2, 3, 6  
**Directorio:** `02_Modelado_Matematico/Funcion_de_Transferencia/`

### Objetivo
Obtener los 4 parámetros reales del sistema mediante prueba escalón sobre hardware:

| Parámetro | Símbolo | Unidad | Valor actual (estimado) |
|-----------|---------|--------|------------------------|
| Ganancia estática bomba | K | L/min | 2.5 ← **MEDIR** |
| Constante de tiempo | τ_q | s | 3.0 ← **MEDIR** |
| Retardo de transporte | L | s | 0.8 ← **MEDIR** |
| Área transversal del tanque | A | L/cm | 0.5 ← **MEDIR** |

### Protocolo de ensayo

**Paso 1 — Preparación:**
- Tanque al 30% de nivel (nivel estable, bombas apagadas).
- Exportar datos del Monitor Serie (115200 baud) a CSV.
- Iniciar captura: tiempo, nivel (%), caudal (L/min).

**Paso 2 — Ensayo escalón de caudal (para K, τ_q, L):**
- t=0: activar Bomba 1 desde modo MANUAL (interfaz web).
- Registrar q(t) durante 30 s a 1 Hz.
- Ajustar G_q(s) = K·e^(-Ls) / (τ_q·s + 1) con método de la curva de reacción:
  - K = valor de caudal en régimen permanente (L/min)
  - L = tiempo de retardo inicial (intersección tangente en inflexión)
  - τ_q = tiempo desde fin del retardo hasta 63% del valor final

**Paso 3 — Ensayo de área del tanque (para A):**
- Con caudal q conocido (medido), registrar variación de nivel Δh en tiempo Δt.
- A = (q · Δt) / Δh    [L/cm]   (balance de masa)

**Paso 4 — Actualizar archivos:**
- `02_Modelado_Matematico/Funcion_de_Transferencia/notas_modelado.md` → tabla de valores
- `05_Simulaciones/MATLAB_Simulink/simulacion_caudal.m` → líneas K, tau_q, L, A_tank
- `05_Simulaciones/simulacion_sistema_llenado.py` → sección CONFIG
- `04_Firmware/arduino_uno/include/config_arduino.h` → MAX_DIST_CM con valor real

### Entregables
- [ ] CSV con datos del ensayo escalón (en `06_Resultados_y_Pruebas/Datos_Medicion/`)
- [ ] Tabla de parámetros identificados con incertidumbre
- [ ] Archivos de configuración actualizados con valores reales

---

## ÁREA 2 — MODELADO MATEMÁTICO COMPLETO

**Estado:** 🟡 PARCIAL — falta completar con valores reales  
**Prioridad:** ALTA  
**Directorio:** `02_Modelado_Matematico/`

### Tareas

**2.1 — Función de Transferencia con valores reales**
- Completar tabla de parámetros en `notas_modelado.md`
- Calcular polos y ceros numéricos
- Calcular margen de fase y margen de ganancia con Bode
- Documentar respuesta al escalón esperada (tiempo de subida, sobrepaso, ts)

**2.2 — Espacio de estados numérico**
- Sustituir valores reales en matrices A, B, C, D
- Calcular valores propios numéricos (λ₁, λ₂)
- Calcular número de condición de la matriz de controlabilidad
- Verificar separación de polos

**2.3 — Análisis MATLAB completo**
- Ejecutar `simulacion_caudal.m` con parámetros reales
- Exportar gráficas: step, bode, rlocus (en `06_Resultados_y_Pruebas/Graficas/`)
- Documentar K_lqr resultante

### Entregables
- [ ] `notas_modelado.md` y `notas_espacio_estados.md` completados con valores reales
- [ ] Gráficas MATLAB exportadas (PNG/PDF)
- [ ] K_lqr calculado y documentado

---

## ÁREA 3 — ANÁLISIS DE ESTABILIDAD FORMAL

**Estado:** ⬜ PENDIENTE — directorio vacío  
**Prioridad:** ALTA  
**Directorio:** `02_Modelado_Matematico/Analisis_de_Estabilidad/`

### Archivo a crear: `analisis_estabilidad.md`

**3.1 — Estabilidad en lazo abierto**
- Criterio de Routh-Hurwitz (sin retardo)
- Lugar geométrico de raíces: trazado y análisis
- Diagrama de Bode: margen de fase (φₘ) y margen de ganancia (Gₘ)
- Criterio de Nyquist

**3.2 — Estabilidad con retardo de transporte**
- Análisis de Padé aproximation del retardo e^(-Ls)
- Reducción del margen de fase debida al retardo: Δφ = -L·ω [rad]
- Frecuencia de cruce de ganancia crítica

**3.3 — Estabilidad con histéresis (implementación actual)**
- El sistema con control ON/OFF es no lineal; analizar como ciclo límite
- Amplitud y período de oscilación predichos por el método del balance armónico (describing function)
- Comparar con simulación Python (banda ±5%)

**3.4 — Estabilidad con LQR**
- Polos de lazo cerrado con K_lqr calculado
- Demostración de estabilidad asintótica (todos los valores propios con parte real negativa)
- Verificación del margen de estabilidad garantizado por LQR (≥ 6 dB ganancia, ≥ 60° fase)

### Entregables
- [ ] `analisis_estabilidad.md` con desarrollo completo
- [ ] Gráficas Nyquist y Bode con márgenes marcados

---

## ÁREA 4 — DIAGRAMAS TÉCNICOS

**Estado:** ⬜ PENDIENTE — todos los subdirectorios vacíos  
**Prioridad:** MEDIA  
**Directorio:** `03_Diseno_del_Sistema/`

### 4.1 — Diagrama de Bloques (`Diagrama_de_Bloques/`)
Crear `diagrama_bloques_sistema.md` con diagrama ASCII de alta resolución que incluya:
- Bloque planta (G_bomba, G_tanque)
- Bloque controlador (histéresis / LQR)
- Bloque sensor HC-SR04 (con ruido gaussiano modelado)
- Bloque sensor GFS401 (con cuantización modelada)
- Lazo de realimentación completo
- Perturbaciones externas (drenaje, evaporación)

### 4.2 — Diagrama de Flujo (`Diagrama_de_Flujo/`)
Crear `flujo_firmware_arduino.md`:
- Diagrama de flujo del `loop()` principal
- Diagrama de flujo de `medirNivel()`
- Diagrama de flujo de `ejecutarControl()` (histéresis)
- Diagrama de flujo de `leerComandos()`
- ISR del GFS401

Crear `flujo_firmware_esp32.md`:
- Diagrama de flujo del servidor web
- Flujo de parseo de datos Arduino
- Flujo de detección de timeout

### 4.3 — Esquemáticos Eléctricos (`Esquematicos/`)
Crear `esquematico_conexiones.md` con:
- Tabla de conexiones completa (netlist textual)
- Diagrama esquemático ASCII del divisor de tensión 5V→3.3V
- Conexiones del módulo relé (IN1, IN2, COM, NC, NO)
- Alimentación: reglas de separación GND analógico/digital
- Advertencias de seguridad: aislamiento galvánico relé, TVS en señales largas

### 4.4 — PCB (`PCB/`)
Crear `notas_pcb.md` con lineamientos para diseño PCB futuro:
- Recomendaciones de layout
- Separación zonas de potencia / señal / microcontrolador
- Footprints recomendados

### Entregables
- [ ] `diagrama_bloques_sistema.md`
- [ ] `flujo_firmware_arduino.md` + `flujo_firmware_esp32.md`
- [ ] `esquematico_conexiones.md`
- [ ] `notas_pcb.md`

---

## ÁREA 5 — MEJORAS DE FIRMWARE

**Estado:** 🟡 IDENTIFICADAS — pendiente de implementar  
**Prioridad:** MEDIA-ALTA  

### 5.1 — Arduino Uno: correcciones críticas

**Bug 1: delay() bloqueante en medirNivel()**
```cpp
// ACTUAL (bloqueante — 30 ms por ciclo)
for (uint8_t i = 0; i < LECTURAS_PROMEDIO; i++) {
    ...
    delay(10);   // ← BLOQUEA 10 ms por lectura
}

// PROPUESTA: tomar solo 1 lectura por llamada, promediar en buffer circular
```

**Bug 2: Sin Watchdog Timer**
```cpp
// AGREGAR en setup():
#include <avr/wdt.h>
wdt_enable(WDTO_4S);   // reset si la CPU no responde en 4 s

// AGREGAR en loop() antes de cerrar:
wdt_reset();
```

**Mejora 3: Checksum en protocolo serial**
```
Protocolo propuesto: N:75.3,Q:2.15,B1:1,B2:0,SP:80,M:1,A:0*CRC\n
CRC = XOR de todos los bytes del campo de datos
```

**Mejora 4: Pull-up externo GFS401**
- Agregar R=4.7kΩ entre pin 2 y VCC en esquemático
- Documentar en manual técnico

### 5.2 — ESP32: mejoras de usabilidad

**mDNS:** Agregar `ESP32mDNS` → acceso por `http://llenado.local`  
**OTA:** Over-the-Air updates para actualizar firmware sin USB  
**Logging:** Endpoint `/log` para historial de últimos N estados

### Entregables
- [ ] `controlador_principal_v3.ino` con watchdog y sin delay bloqueante
- [ ] `interfaz_wifi_v2.ino` con mDNS
- [ ] Protocolo serial con checksum documentado

---

## ÁREA 6 — IMPLEMENTACIÓN LQR EN FIRMWARE

**Estado:** ⬜ PENDIENTE — diseño existe en MATLAB, no en firmware  
**Prioridad:** ALTA (objetivo central del curso)  
**Depende de:** Área 1 (parámetros reales), Área 2 (K_lqr calculado)

### Plan de implementación

**Paso 1 — Digitalización del controlador LQR**
El LQR es continuo: u = -K_lqr · x.  
Para Arduino (T = 0.2 s), discretizar por método de Euler o ZOH:
```
u[k] = -K_lqr[0]·(h[k] - h_ref) - K_lqr[1]·q[k] + N_bar·h_ref
```

**Paso 2 — Estructura en firmware**
```cpp
// En config_arduino.h — agregar tras identificación:
#define K_LQR_NIVEL    XX.XXX   // ganancia estado nivel
#define K_LQR_CAUDAL   XX.XXX   // ganancia estado caudal
#define N_BAR          XX.XXX   // precompensación seguimiento

// Nueva función en controlador_principal.ino:
void ejecutarLQR() {
    float error_nivel  = est.nivel_pct - (float)est.setpoint;
    float u = -(K_LQR_NIVEL * error_nivel) - (K_LQR_CAUDAL * est.caudal_lpm)
              + N_BAR * (float)est.setpoint;
    // Saturar u a [0, 1] y aplicar como PWM (si se tiene control PWM de bomba)
    // O convertir a ON/OFF con umbral si se mantiene control por relé
    setBomba(1, u > UMBRAL_PWM_ON);
}
```

**Paso 3 — Selección de modo de control**
Agregar campo `modo_control` al estado: 0=Histéresis, 1=LQR  
Comando nuevo: `C:0` o `C:1` desde ESP32

**Paso 4 — Validación**
- Comparar respuesta LQR vs histéresis en simulación Python primero
- Luego implementar en hardware y medir

### Entregables
- [ ] `controlador_principal_v3.ino` con función `ejecutarLQR()`
- [ ] Actualización de protocolo serial con campo modo_control
- [ ] Comparativa simulada LQR vs histéresis (gráfica Python)

---

## ÁREA 7 — VALIDACIÓN EXPERIMENTAL Y REGISTRO DE DATOS

**Estado:** ⬜ PENDIENTE  
**Prioridad:** MEDIA  
**Directorio:** `06_Resultados_y_Pruebas/`

### Ensayos a realizar con hardware real

| Ensayo | Descripción | Métricas |
|--------|-------------|---------|
| E01 | Arranque desde vacío → SP=80% | tr, tp, Mp, ts, error ss |
| E02 | Perturbación: abrir válvula drenaje 5 s | Δh_max, tiempo recuperación |
| E03 | Cambio de setpoint 80%→50% | tr, sobrepaso negativo |
| E04 | LQR vs Histéresis (mismo SP) | Comparativa energía, oscilación |
| E05 | Fallo de bomba (alarma) | Tiempo detección alarma |

### Formato de registro
- CSV por ensayo: `tiempo_s, nivel_pct, caudal_lpm, bomba1, bomba2, sp, modo, alarma`
- Gráficas matplotlib en `06_Resultados_y_Pruebas/Graficas/`

### Entregables
- [ ] 5 archivos CSV de ensayos (en `Datos_Medicion/`)
- [ ] 5 gráficas comparativas (en `Graficas/`)
- [ ] `analisis_resultados.md` con tabla comparativa y conclusiones

---

## ÁREA 8 — INFORME FINAL ACADÉMICO

**Estado:** ⬜ PENDIENTE — directorio vacío  
**Prioridad:** ALTA  
**Directorio:** `01_Documentacion/Informe_Final/`

### Estructura del informe (`informe_final.md` → exportar a PDF)

```
1. Introducción y objetivos
2. Marco teórico
   2.1 Sistemas de control automático de nivel
   2.2 Representación en espacio de estados
   2.3 Control óptimo LQR
   2.4 Análisis de estabilidad
3. Descripción del sistema
   3.1 Arquitectura hardware
   3.2 Protocolo de comunicación
   3.3 Interfaz HMI web
4. Modelado matemático
   4.1 Identificación experimental de parámetros
   4.2 Funciones de transferencia
   4.3 Representación en espacio de estados
   4.4 Análisis de estabilidad
5. Diseño del controlador
   5.1 Control por histéresis (implementado)
   5.2 Control LQR óptimo (diseño e implementación)
6. Simulaciones
   6.1 Simulación Python (3 escenarios)
   6.2 Análisis MATLAB
7. Resultados experimentales
   7.1 Identificación de parámetros
   7.2 Validación del modelo
   7.3 Comparativa controladores
8. Conclusiones y trabajo futuro
9. Referencias
Apéndices: código fuente completo, esquemáticos
```

### Entregables
- [ ] `informe_final.md` completo (≥ 25 páginas)
- [ ] PDF exportado

---

## ÁREA 9 — PRESENTACIÓN

**Estado:** ⬜ PENDIENTE  
**Prioridad:** MEDIA  
**Directorio:** `01_Documentacion/Presentacion/`

### Estructura de diapositivas (`presentacion.md`)
15–20 diapositivas:
1. Portada
2. Agenda
3. Planteamiento del problema
4. Arquitectura del sistema (diagrama)
5. Hardware: componentes clave
6. Modelado matemático: G(s) y espacio de estados
7. Análisis de estabilidad: Bode, Nyquist
8. Control por histéresis: funcionamiento y limitaciones
9. Diseño LQR: matrices Q, R, ganancias K_lqr
10. Simulación Python: 3 escenarios
11. Resultados experimentales: Ensayo E01
12. Comparativa histéresis vs LQR
13. Interfaz web HMI (captura de pantalla)
14. Conclusiones
15. Trabajo futuro
16. Referencias

### Entregables
- [ ] `presentacion.md` con estructura completa
- [ ] Exportar a PDF o PowerPoint

---

## REGISTRO DE SESIONES

| # | Fecha | Áreas trabajadas | Estado | Bitácora |
|---|-------|-----------------|--------|---------|
| 001 | 2026-06-01 | Protocolo inicial, memoria, hallazgos firmware | ✅ | [sesion_001_bitacora.md](SESIONES/sesion_001_bitacora.md) |

---

## REGLAS DEL PROTOCOLO

1. **Una sesión, un área.** Salvo que el trabajo lo permita naturalmente.
2. **Commit al cerrar cada sesión.** Con mensaje descriptivo del área trabajada.
3. **Actualizar esta tabla** con cada sesión completada.
4. **Nunca marcar como completo sin entregable verificable.**
5. **Los parámetros K, τ_q, L, A son bloqueantes** — las Áreas 2, 3, 6 no se cierran sin medición real.
