# Función de Transferencia del Sistema

## Arquitectura del sistema (v2)

El sistema ampliado tiene **dos variables controladas** (MIMO):

```
          ┌──────────┐     q(t)    ┌────────────┐    h(t)
  u1 ────►│ Bomba 1  ├────────────►│   Tanque   ├────────► y1 = h
          │ (Llenado)│             │  + HC-SR04 │
          └──────────┘             └────────────┘
          ┌──────────┐
  u2 ────►│ Bomba 2  ├──────────────────────────────────────── (descarga)
          │(Descarga)│
          └──────────┘
               │
               └── GFS401 mide q(t)  ──────────────────────── y2 = q
```

---

## Modelo de la Bomba + Tubería (subsistema de caudal)

El caudal responde a la activación de la bomba como un sistema de **primer orden**:

```
        K · e^(-Ls)
G_q(s) = ─────────────
            τ_q·s + 1
```

| Parámetro | Descripción                           | Unidad  |
|-----------|---------------------------------------|---------|
| K         | Ganancia estática (caudal en régimen) | L/min   |
| τ_q       | Constante de tiempo de la bomba       | s       |
| L         | Retardo de transporte en la tubería   | s       |

---

## Modelo del Tanque (subsistema de nivel)

El nivel integra la diferencia de flujos de entrada y salida:

```
          1
G_h(s) = ───
          A·s
```

donde **A** = área de la sección transversal del tanque [L/cm] (o unidades consistentes).

El nivel en función del caudal neto:

```
        q_in(s) - q_out(s)
H(s) = ────────────────────
                A·s
```

---

## Función de transferencia en lazo abierto (canal de llenado)

Concatenando bomba → tanque:

```
                    K · e^(-Ls)
G_total(s) = ──────────────────────────
              A · s · (τ_q · s + 1)
```

Este es un sistema de **tipo 1** (un integrador puro del tanque) → error en régimen permanente = 0 para referencia escalón de nivel.

---

## Procedimiento de identificación experimental

1. Con el tanque a nivel estable, activar Bomba 1 como entrada escalón.
2. Registrar h(t) con el HC-SR04 a 1 Hz durante 60 s.
3. Registrar q(t) con el GFS401 simultáneamente.
4. Ajustar K, τ_q, L al modelo G_q(s) con el método de la curva de reacción.
5. Calcular A dividiendo la variación de volumen entre la variación de nivel.

### Valores a completar (medición real)

| Parámetro | Valor | Unidad |
|-----------|-------|--------|
| K         |       | L/min  |
| τ_q       |       | s      |
| L         |       | s      |
| A         |       | L/cm   |

---

## Diseño del controlador (propuesta)

### Opción 1 — Histéresis (implementada en v2)
Control ON/OFF con banda de histéresis ±5 % sobre el setpoint de nivel.  
Simple, robusto, pero genera oscilaciones permanentes alrededor del setpoint.

### Opción 2 — PID sobre nivel (mejora futura)
```
               (   1        τ_d·s  )
C(s) = K_p · ( 1 + ─────── + ──────── )
               (  τ_i·s    1 + τ_d/N·s )
```
Ajuste por Ziegler-Nichols o por asignación de polos (método del espacio de estados).
