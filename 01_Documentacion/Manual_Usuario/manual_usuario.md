# Manual de Usuario
## Sistema de Llenado de Flujo Continuo

**Universidad Santiago Mariño — Teoría Moderna de Control**  
**Versión:** 2.0 | Fecha: Junio 2026

---

## ¿Qué hace este sistema?

Este sistema llena y controla automáticamente el nivel de agua en un tanque.  
Usa dos sensores para saber exactamente cuánta agua hay y a qué velocidad entra,  
y dos bombas para llenar o vaciar el tanque según se necesite.

Puedes ver el estado del sistema y controlarlo desde tu **teléfono o computadora**  
conectándote a la red WiFi que el sistema crea automáticamente.

---

## Componentes que verás en el sistema

```
┌─────────────────────────────────────────────┐
│               TABLERO DE CONTROL             │
│                                              │
│  ┌──────────┐  ┌──────────┐                 │
│  │ARDUINO   │  │  ESP32   │  ← placas       │
│  │  UNO     │  │  WiFi    │    electrónicas  │
│  └──────────┘  └──────────┘                 │
│         │             │                      │
│      cables        cable USB                 │
└─────────┼───────────────────────────────────┘
          │
    ┌─────┴──────────────────────────────────┐
    │               SISTEMA FÍSICO            │
    │                                         │
    │  ┌───────┐     ┌──────────┐            │
    │  │Tanque │     │Caudalím. │ GFS401      │
    │  │ con   │     │ GFS401   │ (en tubería)│
    │  │HC-SR04│     └──────────┘            │
    │  │ (tapa)│                              │
    │  └───────┘                              │
    │                                         │
    │  [Bomba 1 Llenado]  [Bomba 2 Descarga] │
    └─────────────────────────────────────────┘
```

| Componente visible     | Función                                              |
|------------------------|------------------------------------------------------|
| Tanque principal       | Depósito cuyo nivel se controla                      |
| HC-SR04 (tapa tanque)  | Sensor que mide el nivel de agua (apunta hacia abajo)|
| GFS401 (en tubería)    | Sensor que mide cuánta agua pasa por la tubería      |
| Bomba 1                | Llena el tanque                                      |
| Bomba 2                | Descarga o recircula el agua                         |
| Arduino Uno            | Cerebro del sistema; ejecuta el control              |
| ESP32                  | Crea la red WiFi; sirve la app de control            |

---

## Encendido del Sistema

### Paso 1 — Verificar el agua
Asegurarse de que el reservorio de agua esté lleno antes de encender las bombas.  
Nunca encender una bomba sin agua; puede dañarse en segundos.

### Paso 2 — Conectar la alimentación
1. Conectar el cable USB del **Arduino Uno** a la fuente de 5V (o al computador).
2. Conectar el cable USB del **ESP32** a su fuente (o al mismo computador).
3. Conectar la fuente de alimentación de las **bombas** (5V o 12V según modelo).

### Paso 3 — Esperar el inicio
El sistema tarda aproximadamente **5 segundos** en arrancar completamente.  
Durante este tiempo, los relés pueden hacer un pequeño clic — es normal.

---

## Conexión a la Aplicación Web

### Desde un teléfono celular:

1. Abrir **Configuración → WiFi** en el teléfono.
2. Buscar la red: **`ESP32-Llenado`**
3. Conectar con la contraseña: **`control2026`**
4. Abrir el **navegador web** (Chrome, Safari, Firefox).
5. Escribir en la barra de dirección: **`192.168.4.1`** y presionar Entrar.
6. La aplicación de control debe aparecer en pantalla.

### Desde una computadora:
Mismo procedimiento: conectar al WiFi `ESP32-Llenado` y abrir `192.168.4.1` en el navegador.

> **Nota:** Al conectarte al WiFi del ESP32, el teléfono no tendrá internet.  
> Esto es normal; la app funciona de forma local sin internet.

---

## Pantalla Principal de la Aplicación

```
┌─────────────────────────────────────┐
│        Sistema de Llenado           │
├─────────────────────────────────────┤
│  NIVEL DEL TANQUE                   │
│  ┌──┐                               │
│  │  │ ← barra azul                  │
│  │▓▓│   (sube y baja en tiempo real)│   75.3 %
│  │▓▓│                               │
│  │──│ ← línea naranja = setpoint    │
│  │  │                               │   Setpoint: 80%
│  └──┘                               │
├─────────────────────────────────────┤
│  SENSORES                           │
│  Caudal:          2.15 L/min        │
├─────────────────────────────────────┤
│  BOMBAS                             │
│  ● Bomba 1 (Llenado)  [ON] [OFF]   │
│  ○ Bomba 2 (Descarga) [ON] [OFF]   │
│  ● = verde (encendida)              │
│  ○ = gris  (apagada)                │
├─────────────────────────────────────┤
│  SETPOINT DE NIVEL                  │
│  [────────●────────────────]  80%   │
│   0%                        100%    │
├─────────────────────────────────────┤
│  MODO DE OPERACIÓN                  │
│  [        AUTO        ]             │
├─────────────────────────────────────┤
│  Actualizado: 10:45:32              │
└─────────────────────────────────────┘
```

### Descripción de cada elemento

| Elemento                | Descripción                                                        |
|-------------------------|--------------------------------------------------------------------|
| Barra azul (tanque)     | Representa el nivel actual de agua; sube y baja en tiempo real    |
| Línea naranja           | Indica el setpoint (nivel objetivo)                                |
| Número de porcentaje    | Nivel exacto en % (0% = vacío, 100% = lleno)                      |
| Caudal                  | Velocidad del agua que entra, en litros por minuto                 |
| Indicador Bomba (●/○)  | Verde = bomba encendida, Gris = bomba apagada                      |
| Botones ON/OFF          | Control manual de cada bomba (solo activo en modo MANUAL)         |
| Slider de setpoint      | Deslizar para cambiar el nivel objetivo (0–100%)                   |
| Botón AUTO/MANUAL       | Cambia entre control automático y manual                           |
| Línea de tiempo         | Hora de la última actualización de datos                           |

---

## Modo AUTO (recomendado para operación normal)

En modo **AUTO**, el sistema controla las bombas por sí solo:

- La **Bomba 1** (llenado) se enciende cuando el nivel baja del **setpoint − 5%**.
- La **Bomba 1** se apaga cuando el nivel sube del **setpoint + 5%**.
- La **Bomba 2** permanece apagada (solo se activa manualmente en modo AUTO).

### Ejemplo con setpoint = 80%:
```
Nivel < 75%  →  Bomba 1 ENCIENDE  (empieza a llenar)
Nivel > 85%  →  Bomba 1 APAGA     (deja de llenar)
75% < Nivel < 85%  →  Sin cambio  (banda de histéresis)
```

### Cómo cambiar el setpoint en modo AUTO:
1. Deslizar el **slider de setpoint** al valor deseado (ej. 60%).
2. El sistema ajusta automáticamente los puntos de encendido y apagado.
3. No es necesario cambiar a modo MANUAL para ajustar el setpoint.

---

## Modo MANUAL

En modo **MANUAL**, tú controlas directamente cada bomba:

1. Presionar el botón **MANUAL** en la app (cambia de azul a naranja).
2. Usar los botones **ON / OFF** de cada bomba para controlarlas.
3. El sistema **no** actuará automáticamente mientras estés en MANUAL.

### Cuándo usar modo MANUAL:
- Para vaciar el tanque completamente (Bomba 2 ON).
- Para pruebas de funcionamiento del sistema.
- Para llenar manualmente sin control automático.

> **Precaución:** En modo MANUAL, el sistema no protege contra desbordamiento.  
> Estar atento al nivel del tanque mientras se opera manualmente.

---

## Alarma del Sistema

Si aparece una barra de color **rojo** en la parte superior de la app con el mensaje:

```
⚠ ALARMA: Bomba 1 activa sin caudal detectado
```

Significa que la Bomba 1 está encendida pero no se detecta flujo de agua.

### Causas posibles:
| Causa                                | Acción a tomar                              |
|--------------------------------------|---------------------------------------------|
| El reservorio de agua está vacío     | Apagar la bomba y rellenar el reservorio    |
| La manguera está doblada o tapada    | Revisar y enderezar las mangueras           |
| La bomba está dañada                 | Verificar la bomba con el técnico           |
| El caudalímetro tiene burbujas       | Purgue el sistema llenando la tubería       |

### Cómo silenciar la alarma:
La alarma desaparece sola cuando el caudal supera 0.5 L/min o cuando la bomba 1 se apaga.

---

## Apagado del Sistema

### Apagado normal:
1. En la app, cambiar a modo **MANUAL**.
2. Apagar ambas bombas con los botones **OFF**.
3. Desconectar la fuente de las bombas.
4. Desconectar los cables USB del Arduino y ESP32.

### En caso de emergencia:
Desconectar directamente la fuente de alimentación de las bombas.  
El sistema no dañará ningún componente al apagarse abruptamente.

---

## Indicadores de Estado de la App

| Indicador                 | Significado                                          |
|---------------------------|------------------------------------------------------|
| Hora actualizada (verde)  | Sistema funcionando correctamente                    |
| "Sin conexión" (rojo)     | El ESP32 no recibe datos del Arduino (revisar cables)|
| Nivel en 0% constante     | HC-SR04 sin respuesta o cable suelto                 |
| Caudal siempre 0          | GFS401 sin respuesta o cable suelto en pin 2         |
| Bomba no responde         | Revisar cables del relé o firmware del Arduino       |

---

## Preguntas Frecuentes

**¿Puedo usar la app desde fuera de casa?**  
No. La app solo funciona cuando el teléfono está conectado al WiFi del ESP32 (red local).

**¿Qué pasa si cierro la app?**  
Si el sistema está en modo AUTO, sigue funcionando normalmente sin la app.  
Si estaba en modo MANUAL con bombas encendidas, estas siguen activas.

**¿Puedo conectar varios teléfonos al mismo tiempo?**  
Sí. Varios dispositivos pueden conectarse al WiFi del ESP32 y ver la app simultáneamente. Solo el último que envíe un comando tendrá efecto.

**¿Cómo cambio la contraseña del WiFi?**  
Modificar la línea `#define WIFI_PASS` en el archivo `config_esp32.h` y recargar el firmware al ESP32.

**¿Qué hago si el nivel no coincide con la realidad?**  
Medir con una regla la distancia real del sensor HC-SR04 al fondo del tanque vacío, y actualizar `MAX_DIST_CM` en `config_arduino.h`.

**¿El sistema funciona si se va la luz y vuelve?**  
Al restaurarse la alimentación, el sistema arranca en modo **AUTO** con el setpoint predeterminado (80%). Las bombas se activan si el nivel lo requiere.

---

## Datos de Acceso Rápido

| Dato                | Valor              |
|---------------------|--------------------|
| Red WiFi            | ESP32-Llenado      |
| Contraseña WiFi     | control2026        |
| Dirección de la app | 192.168.4.1        |
| Setpoint por defecto| 80 %               |
| Banda de histéresis | ± 5 %              |

---

*Manual preparado para el proyecto académico de Teoría Moderna de Control.*  
*Universidad Santiago Mariño — Junio 2026*
