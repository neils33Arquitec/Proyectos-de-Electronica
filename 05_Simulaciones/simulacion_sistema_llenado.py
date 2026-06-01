#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════╗
║        SIMULACIÓN — SISTEMA DE LLENADO DE FLUJO CONTINUO            ║
║        Universidad Santiago Mariño                                   ║
║        Asignatura: Teoría Moderna de Control                         ║
╠══════════════════════════════════════════════════════════════════════╣
║  Replica el comportamiento EXACTO del firmware:                      ║
║    • controlador_principal.ino  (Arduino Uno)                        ║
║    • config_arduino.h                                                ║
║                                                                      ║
║  Modelo físico:                                                      ║
║    • Bomba + tubería  →  sistema de primer orden  G_q(s)             ║
║    • Tanque           →  integrador puro          G_h(s)             ║
║    • HC-SR04          →  medición con ruido gaussiano                ║
║    • GFS401           →  conteo de pulsos simulado                   ║
║                                                                      ║
║  Uso:                                                                ║
║    python simulacion_sistema_llenado.py                              ║
║    python simulacion_sistema_llenado.py --escenario 2                ║
╚══════════════════════════════════════════════════════════════════════╝
"""

import sys
import argparse
import numpy as np
# Forzar UTF-8 en consola Windows para caracteres especiales
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
from dataclasses import dataclass, field
from typing import List, Tuple, Optional

# ──────────────────────────────────────────────────────────────────────────────
# COLORES ANSI para consola
# ──────────────────────────────────────────────────────────────────────────────
R  = '\033[91m';  G  = '\033[92m';  Y  = '\033[93m'
B  = '\033[94m';  C  = '\033[96m';  W  = '\033[97m'
DIM = '\033[2m';  BOLD = '\033[1m'; RST = '\033[0m'

# ──────────────────────────────────────────────────────────────────────────────
# CONFIGURACIÓN — reflejo exacto de config_arduino.h y constantes del firmware
# ──────────────────────────────────────────────────────────────────────────────

# --- Parámetros del controlador (config_arduino.h) ---
HISTERESIS_PCT     = 5        # ±% banda de histéresis
SETPOINT_DEFAULT   = 80       # % — nivel objetivo por defecto
CAUDAL_MIN_ALARMA  = 0.5      # L/min — umbral de alarma bomba sin caudal
T_CONTROL_S        = 0.200    # s — período lectura HC-SR04
T_ENVIO_S          = 1.000    # s — período envío serial al ESP32
FACTOR_GFS401      = 7.5      # pulsos / (L/min)

# --- Parámetros físicos del sistema (actualizar con medición experimental) ---
K_BOMBA1   = 2.5    # L/min — caudal estático bomba 1 (llenado)
K_BOMBA2   = 3.0    # L/min — caudal estático bomba 2 (descarga)
TAU_Q      = 3.0    # s     — constante de tiempo bomba + tubería
V_TANQUE   = 15.0   # L     — volumen total del tanque
RUIDO_HC   = 0.4    # %     — desviación estándar ruido sensor HC-SR04

# --- Parámetros de simulación ---
T_SIM_DEFAULT = 150   # s — duración por defecto
DT            = 0.05  # s — paso de integración Euler


# ──────────────────────────────────────────────────────────────────────────────
# ESTRUCTURAS DE DATOS
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class EstadoSistema:
    """Estado interno del sistema en un instante t."""
    nivel_real:  float = 0.0    # % — nivel real del tanque
    nivel_med:   float = 0.0    # % — nivel medido por HC-SR04 (con ruido)
    q1:          float = 0.0    # L/min — caudal actual bomba 1
    q2:          float = 0.0    # L/min — caudal actual bomba 2
    bomba1:      bool  = False
    bomba2:      bool  = False
    setpoint:    float = float(SETPOINT_DEFAULT)
    modo_auto:   bool  = True
    alarma:      bool  = False

@dataclass
class Registro:
    """Una muestra guardada cada T_ENVIO_S (replica del envío serial)."""
    t:       float
    nivel:   float
    caudal:  float
    bomba1:  int
    bomba2:  int
    sp:      float
    alarma:  int
    evento:  str = ""


# ──────────────────────────────────────────────────────────────────────────────
# CONTROLADOR — replica EXACTA de controlador_principal.ino
# ──────────────────────────────────────────────────────────────────────────────

def set_bomba(estado: EstadoSistema, n: int, on: bool) -> None:
    """Replica de setBomba() en el firmware."""
    if n == 1:
        estado.bomba1 = on
    else:
        estado.bomba2 = on

def ejecutar_control(estado: EstadoSistema) -> str:
    """
    Replica exacta de ejecutarControl() del firmware.
    Usa el nivel MEDIDO (con ruido del HC-SR04), igual que el Arduino real.
    """
    sp    = estado.setpoint
    nivel = estado.nivel_med   # el Arduino usa el nivel medido, no el real
    evento = ""

    if nivel < (sp - HISTERESIS_PCT):
        if not estado.bomba1:
            set_bomba(estado, 1, True)
            evento = (f"{G}Bomba 1 ON {RST} "
                      f"nivel={nivel:.1f}% < SP−HIST={sp-HISTERESIS_PCT:.0f}%")

    elif nivel > (sp + HISTERESIS_PCT):
        if estado.bomba1:
            set_bomba(estado, 1, False)
            evento = (f"{Y}Bomba 1 OFF{RST} "
                      f"nivel={nivel:.1f}% > SP+HIST={sp+HISTERESIS_PCT:.0f}%")

    return evento


# ──────────────────────────────────────────────────────────────────────────────
# MODELO FÍSICO
# ──────────────────────────────────────────────────────────────────────────────

def actualizar_fisica(estado: EstadoSistema, dt: float) -> None:
    """
    Integra la dinámica del sistema en un paso dt:
      Caudal:  dq/dt = -(1/τ)·q + (K/τ)·u   [primer orden]
      Nivel:   dh/dt = (q_in - q_out) · 100 / V_tanque / 60  [integrador]
    """
    u1 = 1.0 if estado.bomba1 else 0.0
    u2 = 1.0 if estado.bomba2 else 0.0

    # Dinámica de caudal (Euler explícito)
    dq1 = (-(1.0 / TAU_Q) * estado.q1 + (K_BOMBA1 / TAU_Q) * u1)
    dq2 = (-(1.0 / TAU_Q) * estado.q2 + (K_BOMBA2 / TAU_Q) * u2)
    estado.q1 = max(0.0, estado.q1 + dq1 * dt)
    estado.q2 = max(0.0, estado.q2 + dq2 * dt)

    # Dinámica del nivel (tanque como integrador)
    flujo_neto_lpm = estado.q1 - estado.q2                       # L/min
    d_nivel = flujo_neto_lpm * 100.0 / V_TANQUE * (dt / 60.0)   # % por paso
    estado.nivel_real = float(np.clip(estado.nivel_real + d_nivel, 0.0, 100.0))

def medir_hcsr04(nivel_real: float) -> float:
    """Simula la lectura del HC-SR04 con ruido gaussiano."""
    return float(np.clip(nivel_real + np.random.normal(0.0, RUIDO_HC), 0.0, 100.0))

def medir_gfs401(caudal_real: float) -> float:
    """Simula el conteo de pulsos del GFS401 en T_ENVIO_S = 1 s."""
    pulsos = caudal_real * FACTOR_GFS401            # pulsos acumulados en 1 s
    pulsos_enteros = int(pulsos + np.random.normal(0, 0.3))   # error de conteo
    return max(0.0, pulsos_enteros / FACTOR_GFS401)


# ──────────────────────────────────────────────────────────────────────────────
# MOTOR DE SIMULACIÓN
# ──────────────────────────────────────────────────────────────────────────────

def simular(
    setpoint:       float = SETPOINT_DEFAULT,
    nivel_inicial:  float = 0.0,
    duracion:       float = T_SIM_DEFAULT,
    eventos_manual: Optional[List[Tuple[float, str, bool]]] = None,
    verbose:        bool  = True
) -> List[Registro]:
    """
    Ejecuta la simulación completa del sistema.

    Parámetros
    ----------
    setpoint       : nivel objetivo en %
    nivel_inicial  : nivel del tanque al inicio en %
    duracion       : segundos a simular
    eventos_manual : lista de (t_s, 'bomba1'|'bomba2'|'setpoint', valor)
                     Ejemplo: [(60.0, 'bomba2', True), (90.0, 'bomba2', False)]
    verbose        : imprimir salida serial por consola
    """
    estado = EstadoSistema(
        nivel_real = float(nivel_inicial),
        nivel_med  = float(nivel_inicial),
        setpoint   = float(setpoint)
    )

    registros: List[Registro] = []
    eventos_manual = eventos_manual or []

    t_ultimo_control = -T_CONTROL_S
    t_ultimo_envio   = -T_ENVIO_S

    if verbose:
        _banner(setpoint, nivel_inicial, duracion)

    t = 0.0
    n_steps = int(duracion / DT) + 1

    for _ in range(n_steps):
        # ── Aplicar eventos manuales programados ─────────────────────────────
        for ev_t, ev_key, ev_val in eventos_manual:
            if abs(t - ev_t) < DT / 2:
                if ev_key == 'bomba1':
                    estado.modo_auto = False
                    set_bomba(estado, 1, bool(ev_val))
                elif ev_key == 'bomba2':
                    set_bomba(estado, 2, bool(ev_val))
                elif ev_key == 'setpoint':
                    estado.setpoint = float(ev_val)

        # ── Lectura HC-SR04 y control (cada T_CONTROL_S) ─────────────────────
        evento = ""
        if (t - t_ultimo_control) >= T_CONTROL_S - 1e-9:
            t_ultimo_control = t
            estado.nivel_med = medir_hcsr04(estado.nivel_real)
            if estado.modo_auto:
                evento = ejecutar_control(estado)
            estado.alarma = estado.bomba1 and (estado.q1 < CAUDAL_MIN_ALARMA)

        # ── Dinámica física (cada DT) ─────────────────────────────────────────
        actualizar_fisica(estado, DT)

        # ── Muestreo y envío serial (cada T_ENVIO_S) ─────────────────────────
        if (t - t_ultimo_envio) >= T_ENVIO_S - 1e-9:
            t_ultimo_envio = t
            caudal_med = medir_gfs401(estado.q1)

            reg = Registro(
                t      = round(t, 2),
                nivel  = round(estado.nivel_real, 2),
                caudal = round(caudal_med, 2),
                bomba1 = int(estado.bomba1),
                bomba2 = int(estado.bomba2),
                sp     = estado.setpoint,
                alarma = int(estado.alarma),
                evento = evento
            )
            registros.append(reg)

            if verbose:
                _print_serial(reg)

        t = round(t + DT, 6)

    if verbose:
        _reporte(registros)

    return registros


# ──────────────────────────────────────────────────────────────────────────────
# SALIDA POR CONSOLA
# ──────────────────────────────────────────────────────────────────────────────

def _banner(sp: float, ni: float, dur: float) -> None:
    sep = f"{DIM}{'-'*72}{RST}"
    print(f"\n{BOLD}{'='*72}{RST}")
    print(f"{BOLD}{C}{'SIMULACION - SISTEMA DE LLENADO DE FLUJO CONTINUO':^72}{RST}")
    print(f"{W}{'Universidad Santiago Marino  |  Teoria Moderna de Control':^72}{RST}")
    print(f"{DIM}{'Replica de: controlador_principal.ino + config_arduino.h':^72}{RST}")
    print(f"{BOLD}{'='*72}{RST}")
    print(f"  {DIM}Parametros fisicos:{RST}  "
          f"K_bomba1={K_BOMBA1} L/min  |  tau={TAU_Q}s  |  V={V_TANQUE}L")
    print(f"  {DIM}Parametros control:{RST}  "
          f"SP={sp:.0f}%  |  Histeresis=+-{HISTERESIS_PCT}%  |  "
          f"Nivel inicial={ni:.0f}%  |  Duracion={dur:.0f}s")
    print(sep)
    print(f"  {DIM}{'t (s)':>7}   {'Salida Serial Arduino (N,Q,B1,B2,SP,M,A)':45}   Evento{RST}")
    print(sep)

def _print_serial(r: Registro) -> None:
    serial = (f"N:{r.nivel:.1f},Q:{r.caudal:.2f},"
              f"B1:{r.bomba1},B2:{r.bomba2},"
              f"SP:{r.sp:.0f},M:1,A:{r.alarma}")

    t_str = f"{B}[{r.t:6.1f}s]{RST}"

    if r.alarma:
        serial_col = f"{R}{serial}{RST}"
    elif r.bomba1:
        serial_col = f"{C}{serial}{RST}"
    else:
        serial_col = f"{DIM}{serial}{RST}"

    ev_str = f"  {Y}<< {r.evento}{RST}" if r.evento else ""
    print(f"  {t_str}  {serial_col}{ev_str}")

def _reporte(registros: List[Registro]) -> None:
    if not registros:
        return

    niveles  = np.array([r.nivel  for r in registros])
    caudales = np.array([r.caudal for r in registros])
    b1s      = np.array([r.bomba1 for r in registros])
    alarmas  = [r.alarma for r in registros]
    tiempos  = [r.t      for r in registros]

    # Tiempo en alcanzar el setpoint por primera vez
    sp_idx = np.where(niveles >= registros[0].sp)[0]
    t_sp   = tiempos[sp_idx[0]] if len(sp_idx) > 0 else None

    # Ciclos ON/OFF
    ciclos = sum(1 for i in range(1, len(b1s)) if b1s[i] == 1 and b1s[i-1] == 0)

    sep = f"{DIM}{'-'*72}{RST}"
    print(f"\n{sep}")
    print(f"{BOLD}{W}{'REPORTE FINAL':^72}{RST}")
    print(sep)

    def fila(label, valor):
        print(f"  {DIM}{label:<32}{RST}  {BOLD}{C}{valor}{RST}")

    fila("Duración simulada",          f"{tiempos[-1]:.0f} s")
    fila("Nivel inicial / final",       f"{niveles[0]:.1f}% -> {niveles[-1]:.1f}%")
    fila("Nivel mín / máx",             f"{niveles.min():.1f}% / {niveles.max():.1f}%")
    fila("Tiempo en alcanzar setpoint", f"{t_sp:.1f} s" if t_sp else "No alcanzado")
    fila("Caudal promedio (bomba ON)",  f"{caudales[b1s==1].mean():.2f} L/min" if b1s.any() else "—")
    fila("Caudal máximo registrado",    f"{caudales.max():.2f} L/min")
    fila("Ciclos ON/OFF Bomba 1",       f"{ciclos}")
    fila("Muestras con alarma",         f"{sum(alarmas)}")
    fila("Paso de integración",         f"{DT*1000:.0f} ms")
    print(f"{sep}\n")


# ──────────────────────────────────────────────────────────────────────────────
# VISUALIZACIÓN
# ──────────────────────────────────────────────────────────────────────────────

def graficar(registros: List[Registro], setpoint: float, titulo_escenario: str = "") -> None:
    if not registros:
        print(f"{R}Sin registros para graficar.{RST}")
        return

    t       = np.array([r.t      for r in registros])
    nivel   = np.array([r.nivel  for r in registros])
    caudal  = np.array([r.caudal for r in registros])
    b1      = np.array([r.bomba1 for r in registros])
    b2      = np.array([r.bomba2 for r in registros])
    alarma  = np.array([r.alarma for r in registros])

    # ── Estilo ────────────────────────────────────────────────────────────────
    BG      = '#0d1117'
    CARD    = '#161b22'
    GRID    = '#21262d'
    AZUL    = '#388bfd'
    VERDE   = '#3fb950'
    NARANJA = '#f0883e'
    ROJO    = '#f85149'
    CIAN    = '#58a6ff'
    GRIS    = '#8b949e'

    plt.rcParams.update({
        'figure.facecolor':  BG,
        'axes.facecolor':    CARD,
        'axes.edgecolor':    GRID,
        'axes.labelcolor':   GRIS,
        'xtick.color':       GRIS,
        'ytick.color':       GRIS,
        'grid.color':        GRID,
        'text.color':        '#e6edf3',
        'legend.facecolor':  CARD,
        'legend.edgecolor':  GRID,
    })

    fig = plt.figure(figsize=(16, 10))
    fig.patch.set_facecolor(BG)

    gs = gridspec.GridSpec(3, 3, figure=fig, hspace=0.55, wspace=0.38,
                           left=0.07, right=0.97, top=0.91, bottom=0.07)

    titulo = (f"Simulación — Sistema de Llenado de Flujo Continuo\n"
              f"Universidad Santiago Mariño  |  Teoría Moderna de Control"
              + (f"  |  {titulo_escenario}" if titulo_escenario else ""))
    fig.suptitle(titulo, fontsize=12, fontweight='bold', color=CIAN, y=0.97)

    ax_n  = fig.add_subplot(gs[0, 0:2])   # Nivel (ancho)
    ax_q  = fig.add_subplot(gs[1, 0:2])   # Caudal
    ax_b  = fig.add_subplot(gs[2, 0:2])   # Bombas + alarma
    ax_tk = fig.add_subplot(gs[0:2, 2])   # Tanque visual
    ax_st = fig.add_subplot(gs[2, 2])     # Estadísticas

    # ── Gráfica 1: Nivel ──────────────────────────────────────────────────────
    ax_n.plot(t, nivel, color=AZUL, linewidth=2.0, label='Nivel h(t)', zorder=3)
    ax_n.axhline(setpoint, color=NARANJA, linewidth=1.8, linestyle='--',
                 label=f'Setpoint ({setpoint:.0f}%)', zorder=4)
    ax_n.axhline(setpoint + HISTERESIS_PCT, color=NARANJA, linewidth=0.8,
                 linestyle=':', alpha=0.6, zorder=4)
    ax_n.axhline(setpoint - HISTERESIS_PCT, color=NARANJA, linewidth=0.8,
                 linestyle=':', alpha=0.6, zorder=4)
    ax_n.fill_between(t, setpoint - HISTERESIS_PCT, setpoint + HISTERESIS_PCT,
                       alpha=0.07, color=NARANJA, label=f'Histéresis ±{HISTERESIS_PCT}%')

    # Sombrear zonas donde la bomba 1 está activa
    for i in range(len(t) - 1):
        if b1[i] == 1:
            ax_n.axvspan(t[i], t[i+1], alpha=0.04, color=CIAN)

    ax_n.set_xlim(t[0], t[-1])
    ax_n.set_ylim(-2, 108)
    ax_n.set_ylabel('Nivel (%)')
    ax_n.set_title('Nivel del Tanque  h(t)', pad=6, fontsize=10)
    ax_n.legend(fontsize=8, loc='lower right', ncol=3)
    ax_n.grid(True, linewidth=0.5)
    ax_n.set_xlabel('Tiempo (s)')

    # ── Gráfica 2: Caudal ─────────────────────────────────────────────────────
    ax_q.plot(t, caudal, color=VERDE, linewidth=2.0, label='Caudal q(t)')
    ax_q.axhline(CAUDAL_MIN_ALARMA, color=ROJO, linewidth=1.0, linestyle=':',
                 alpha=0.9, label=f'Umbral alarma ({CAUDAL_MIN_ALARMA} L/min)')
    ax_q.set_xlim(t[0], t[-1])
    ax_q.set_ylim(bottom=0)
    ax_q.set_ylabel('Caudal (L/min)')
    ax_q.set_title('Caudal GFS401  q(t)', pad=6, fontsize=10)
    ax_q.legend(fontsize=8)
    ax_q.grid(True, linewidth=0.5)
    ax_q.set_xlabel('Tiempo (s)')

    # ── Gráfica 3: Bombas y alarma ────────────────────────────────────────────
    ax_b.fill_between(t, b1.astype(float), step='post', alpha=0.6,
                       color=CIAN, label='Bomba 1 (Llenado)')
    ax_b.fill_between(t, (b2 * 0.7).astype(float), step='post', alpha=0.5,
                       color=NARANJA, label='Bomba 2 (Descarga)')
    ax_b.fill_between(t, (alarma * 0.4).astype(float), step='post', alpha=0.7,
                       color=ROJO, label='Alarma')
    ax_b.set_xlim(t[0], t[-1])
    ax_b.set_ylim(-0.05, 1.15)
    ax_b.set_yticks([0, 0.4, 0.7, 1.0])
    ax_b.set_yticklabels(['OFF', 'ALARMA', 'B2', 'B1'])
    ax_b.set_title('Estado Bombas y Alarma', pad=6, fontsize=10)
    ax_b.legend(fontsize=8, loc='upper right', ncol=3)
    ax_b.grid(True, linewidth=0.5)
    ax_b.set_xlabel('Tiempo (s)')

    # ── Tanque: visualización del estado final ────────────────────────────────
    ax_tk.set_facecolor(BG)
    ax_tk.set_xlim(0, 1); ax_tk.set_ylim(0, 1)
    ax_tk.set_xticks([]); ax_tk.set_yticks([])
    ax_tk.spines[:].set_color(GRID)

    nf = nivel[-1]
    h_water = nf / 100.0 * 0.80   # escala interna 0–0.80

    # Tanque vacío de fondo
    ax_tk.fill_between([0.15, 0.85], [0.08], [0.88],
                        color='#0a0f14', linewidth=0, zorder=1)
    # Agua
    ax_tk.fill_between([0.15, 0.85], [0.08], [0.08 + h_water],
                        color='#1f6feb', alpha=0.80, linewidth=0, zorder=2)
    # Espejo del agua (brillo)
    ax_tk.fill_between([0.15, 0.85], [0.08 + h_water - 0.01], [0.08 + h_water],
                        color='#58a6ff', alpha=0.4, linewidth=0, zorder=3)
    # Paredes del tanque
    for xv in [0.15, 0.85]:
        ax_tk.plot([xv, xv], [0.08, 0.88], color='#30363d', linewidth=3, zorder=4)
    ax_tk.plot([0.15, 0.85], [0.08, 0.08], color='#30363d', linewidth=3, zorder=4)

    # Línea del setpoint
    sp_y = setpoint / 100.0 * 0.80 + 0.08
    ax_tk.plot([0.15, 0.85], [sp_y, sp_y], color=NARANJA,
               linewidth=1.8, linestyle='--', zorder=5)
    ax_tk.text(0.87, sp_y, f'SP\n{setpoint:.0f}%', va='center',
               color=NARANJA, fontsize=7.5)

    # Banda de histéresis
    h_hi = (setpoint + HISTERESIS_PCT) / 100.0 * 0.80 + 0.08
    h_lo = (setpoint - HISTERESIS_PCT) / 100.0 * 0.80 + 0.08
    ax_tk.fill_between([0.15, 0.85], [h_lo, h_lo], [h_hi, h_hi],
                        color=NARANJA, alpha=0.08, zorder=3)

    # HC-SR04 en la tapa
    ax_tk.add_patch(mpatches.FancyBboxPatch(
        (0.35, 0.88), 0.30, 0.07, boxstyle='round,pad=0.01',
        facecolor='#21262d', edgecolor='#30363d', linewidth=1.5, zorder=6))
    ax_tk.text(0.50, 0.915, 'HC-SR04', ha='center', va='center',
               color=GRIS, fontsize=7.5, fontweight='bold', zorder=7)

    # Flecha de medición del sensor
    ax_tk.annotate('', xy=(0.50, 0.08 + h_water + 0.01),
                    xytext=(0.50, 0.88),
                    arrowprops=dict(arrowstyle='<->', color=ROJO,
                                    lw=1.2, shrinkA=3, shrinkB=3), zorder=6)

    # Porcentaje en el centro del agua
    cy = 0.08 + h_water / 2
    if h_water > 0.08:
        ax_tk.text(0.50, cy, f'{nf:.1f}%', ha='center', va='center',
                   fontsize=18, fontweight='bold', color='white', zorder=8)

    # Indicadores de bombas
    col_b1 = VERDE if registros[-1].bomba1 else GRIS
    col_b2 = VERDE if registros[-1].bomba2 else GRIS
    ax_tk.text(0.50, 0.03, f'B1 {"●" if registros[-1].bomba1 else "○"}   '
               f'B2 {"●" if registros[-1].bomba2 else "○"}',
               ha='center', color='white', fontsize=10, zorder=8)

    ax_tk.set_title('Estado Final del Tanque', pad=6, fontsize=10, color='#e6edf3')

    # ── Estadísticas en texto ─────────────────────────────────────────────────
    ax_st.set_facecolor(CARD)
    ax_st.axis('off')
    ax_st.set_title('Reporte', pad=6, fontsize=10, color='#e6edf3')

    sp_idx = np.where(nivel >= setpoint)[0]
    t_sp   = t[sp_idx[0]] if len(sp_idx) > 0 else None
    ciclos = sum(1 for i in range(1, len(b1)) if b1[i] == 1 and b1[i-1] == 0)
    q_on   = caudal[b1 == 1]

    stats = [
        ('Nivel inicial',        f'{nivel[0]:.1f} %'),
        ('Nivel final',          f'{nivel[-1]:.1f} %'),
        ('Nivel máximo',         f'{nivel.max():.1f} %'),
        ('t -> setpoint',         f'{t_sp:.1f} s' if t_sp else 'No alcanzado'),
        ('Caudal promedio',      f'{q_on.mean():.2f} L/min' if len(q_on) else '—'),
        ('Caudal máximo',        f'{caudal.max():.2f} L/min'),
        ('Ciclos B1 ON/OFF',     str(ciclos)),
        ('Muestras alarma',      str(int(alarma.sum()))),
        ('Duración',             f'{t[-1]:.0f} s'),
    ]

    y = 0.95
    for label, val in stats:
        ax_st.text(0.04, y, label, color=GRIS, fontsize=8.5,
                   transform=ax_st.transAxes)
        ax_st.text(0.70, y, val, color=CIAN, fontsize=8.5, fontweight='bold',
                   transform=ax_st.transAxes)
        y -= 0.10

    # Guardar imagen
    out_path = 'simulacion_resultado.png'
    plt.savefig(out_path, dpi=150, bbox_inches='tight', facecolor=BG)
    print(f"{G}Grafica guardada -> {out_path}{RST}\n")
    plt.show()


# ──────────────────────────────────────────────────────────────────────────────
# ESCENARIOS PREDEFINIDOS
# ──────────────────────────────────────────────────────────────────────────────

ESCENARIOS = {
    1: {
        "nombre":        "Arranque desde cero",
        "descripcion":   "Tanque vacio, setpoint 80%, modo AUTO - llenado completo hasta regimen",
        "setpoint":      80,
        "nivel_inicial": 0,
        "duracion":      350,
        "eventos":       [],
    },
    2: {
        "nombre":        "Tanque lleno - drenaje",
        "descripcion":   "Tanque al 100%, setpoint 40%, modo AUTO — observar corte de bomba y drenaje manual",
        "setpoint":      40,
        "nivel_inicial": 100,
        "duracion":      120,
        "eventos":       [
            (30.0,  'bomba2', True),    # a los 30s activar bomba 2 (drenar)
            (80.0,  'bomba2', False),   # a los 80s apagar bomba 2
        ],
    },
    3: {
        "nombre":        "Perturbación externa",
        "descripcion":   "Régimen estable SP=70%, a los 60s se drena 20% del tanque manualmente",
        "setpoint":      70,
        "nivel_inicial": 0,
        "duracion":      200,
        "eventos":       [
            (60.0,  'bomba2', True),    # activar drenaje brusco
            (75.0,  'bomba2', False),   # cortar drenaje → sistema debe recuperarse
            (130.0, 'setpoint', 50.0),  # cambio de setpoint en caliente
        ],
    },
}


# ──────────────────────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='Simulación del Sistema de Llenado — Teoría Moderna de Control')
    parser.add_argument('--escenario', type=int, default=1, choices=ESCENARIOS.keys(),
                        help='Escenario a simular (1, 2 o 3)')
    parser.add_argument('--no-grafica', action='store_true',
                        help='Omitir la generación de gráfica')
    args = parser.parse_args()

    esc = ESCENARIOS[args.escenario]

    print(f"\n{BOLD}{C}Escenario {args.escenario}: {esc['nombre']}{RST}")
    print(f"{DIM}{esc['descripcion']}{RST}")

    registros = simular(
        setpoint       = esc['setpoint'],
        nivel_inicial  = esc['nivel_inicial'],
        duracion       = esc['duracion'],
        eventos_manual = esc['eventos'],
        verbose        = True
    )

    if not args.no_grafica:
        graficar(registros, setpoint=esc['setpoint'],
                 titulo_escenario=esc['nombre'])

if __name__ == '__main__':
    main()
