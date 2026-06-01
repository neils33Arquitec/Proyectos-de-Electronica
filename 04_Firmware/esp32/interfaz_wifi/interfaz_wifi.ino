/*
 * interfaz_wifi.ino
 * ESP32 — Interfaz WiFi del sistema de llenado de flujo continuo
 * Universidad Santiago Mariño — Teoría Moderna de Control
 *
 * Responsabilidades:
 *   - Recibir datos del Arduino Uno via Serial2 (UART2)
 *   - Crear un punto de acceso WiFi "ESP32-Llenado"
 *   - Servir una aplicación web de control en 192.168.4.1
 *   - Reenviar comandos de la app al Arduino
 *
 * Librerías requeridas (instalar en Arduino IDE):
 *   - WiFi.h        (incluida con el soporte de ESP32)
 *   - WebServer.h   (incluida con el soporte de ESP32)
 *
 * Rutas HTTP:
 *   GET  /       → App web (HTML)
 *   GET  /data   → JSON con estado actual del sistema
 *   POST /cmd    → Enviar comando al Arduino
 */

#include <WiFi.h>
#include <WebServer.h>
#include "../include/config_esp32.h"

// =============================================================================
// App web embebida — sin dependencias externas (funciona sin internet)
// =============================================================================
static const char HTML_APP[] PROGMEM = R"HTMLEND(
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Control de Llenado</title>
<style>
  *{box-sizing:border-box;margin:0;padding:0}
  body{background:#0d1117;color:#e6edf3;font-family:'Segoe UI',Arial,sans-serif;padding:14px;max-width:480px;margin:0 auto}
  h1{color:#58a6ff;text-align:center;font-size:1.3em;padding:14px 0 18px;letter-spacing:1px}
  .card{background:#161b22;border:1px solid #30363d;border-radius:10px;padding:16px;margin-bottom:14px}
  .card-title{font-size:.75em;color:#8b949e;text-transform:uppercase;letter-spacing:.8px;margin-bottom:14px}

  /* Gauge nivel */
  .gauge-row{display:flex;align-items:flex-end;gap:20px}
  .tank{width:56px;height:140px;border:2px solid #30363d;border-radius:6px 6px 4px 4px;overflow:hidden;position:relative;background:#0d1117}
  .water{position:absolute;bottom:0;width:100%;background:linear-gradient(to top,#1f6feb,#388bfd);border-radius:0 0 2px 2px;transition:height .6s ease}
  .sp-line{position:absolute;width:100%;height:2px;background:#f0883e;left:0}
  .gauge-info{flex:1}
  .big-num{font-size:2.8em;font-weight:700;color:#58a6ff;line-height:1}
  .unit{font-size:.85em;color:#8b949e;margin-top:2px}
  .sp-tag{margin-top:10px;font-size:.82em;color:#8b949e}
  .sp-tag span{color:#f0883e;font-weight:600}

  /* Stats */
  .stat-row{display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-bottom:1px solid #21262d}
  .stat-row:last-child{border-bottom:none}
  .stat-label{font-size:.85em;color:#8b949e}
  .stat-val{font-size:1.15em;font-weight:600}

  /* Bombas */
  .pump-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px}
  .pump-box{background:#21262d;border-radius:8px;padding:14px;text-align:center}
  .dot{width:18px;height:18px;border-radius:50%;margin:0 auto 8px}
  .dot-on{background:#3fb950;box-shadow:0 0 8px #3fb950}
  .dot-off{background:#484f58}
  .pump-name{font-size:.8em;color:#8b949e;margin-bottom:10px}
  .btn-row{display:flex;gap:6px}
  .btn{flex:1;padding:7px 0;border:none;border-radius:5px;font-size:.8em;font-weight:600;cursor:pointer;transition:opacity .15s}
  .btn:active{opacity:.7}
  .btn-green{background:#238636;color:#fff}
  .btn-red{background:#b91c1c;color:#fff}

  /* Slider setpoint */
  .sp-row{display:flex;align-items:center;gap:12px;margin-top:4px}
  input[type=range]{flex:1;accent-color:#58a6ff;height:6px}
  .sp-num{min-width:42px;text-align:right;font-weight:700;color:#58a6ff}

  /* Modo */
  .mode-btn{width:100%;padding:12px;border:none;border-radius:8px;font-size:1em;font-weight:700;cursor:pointer;transition:background .2s}
  .m-auto{background:#1f6feb;color:#fff}
  .m-manual{background:#9e6a03;color:#fff}

  /* Alarma */
  .alarm{background:#3d1a1a;border:1px solid #f85149;padding:10px;border-radius:8px;text-align:center;font-size:.85em;color:#f85149;margin-bottom:14px;display:none}

  /* Status */
  .status{text-align:center;font-size:.72em;color:#484f58;margin-top:10px}
  .ok{color:#3fb950}.err{color:#f85149}
</style>
</head>
<body>
<h1>Sistema de Llenado</h1>

<div class="alarm" id="alarm">ALARMA: Bomba 1 activa sin caudal detectado</div>

<div class="card">
  <div class="card-title">Nivel del Tanque</div>
  <div class="gauge-row">
    <div class="tank">
      <div class="water" id="water" style="height:0%"></div>
      <div class="sp-line" id="spLine" style="bottom:80%"></div>
    </div>
    <div class="gauge-info">
      <div class="big-num" id="nivelNum">--</div>
      <div class="unit">% nivel</div>
      <div class="sp-tag">Setpoint: <span id="spTag">80</span>%</div>
    </div>
  </div>
</div>

<div class="card">
  <div class="card-title">Sensores</div>
  <div class="stat-row">
    <span class="stat-label">Caudal</span>
    <span class="stat-val" id="caudalVal">-- L/min</span>
  </div>
</div>

<div class="card">
  <div class="card-title">Bombas</div>
  <div class="pump-grid">
    <div class="pump-box">
      <div class="dot dot-off" id="dot1"></div>
      <div class="pump-name">Bomba 1 (Llenado)</div>
      <div class="btn-row">
        <button class="btn btn-green" onclick="cmd('B1',1)">ON</button>
        <button class="btn btn-red"   onclick="cmd('B1',0)">OFF</button>
      </div>
    </div>
    <div class="pump-box">
      <div class="dot dot-off" id="dot2"></div>
      <div class="pump-name">Bomba 2 (Descarga)</div>
      <div class="btn-row">
        <button class="btn btn-green" onclick="cmd('B2',1)">ON</button>
        <button class="btn btn-red"   onclick="cmd('B2',0)">OFF</button>
      </div>
    </div>
  </div>
</div>

<div class="card">
  <div class="card-title">Setpoint de Nivel</div>
  <div class="sp-row">
    <input type="range" min="0" max="100" value="80" id="spSlider"
           oninput="document.getElementById('spNum').textContent=this.value"
           onchange="cmd('SP',parseInt(this.value))">
    <div class="sp-num"><span id="spNum">80</span>%</div>
  </div>
</div>

<div class="card">
  <div class="card-title">Modo de Operacion</div>
  <button class="mode-btn m-auto" id="modeBtn" onclick="toggleMode()">AUTO</button>
</div>

<div class="status">Actualizado: <span id="ts" class="ok">--</span></div>

<script>
var modoAuto=true;

function cmd(c,v){
  fetch('/cmd',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({cmd:c,val:v})});
}

function toggleMode(){
  modoAuto=!modoAuto;
  cmd('M',modoAuto?1:0);
  refreshMode();
}

function refreshMode(){
  var b=document.getElementById('modeBtn');
  b.textContent=modoAuto?'AUTO':'MANUAL';
  b.className='mode-btn '+(modoAuto?'m-auto':'m-manual');
}

function poll(){
  fetch('/data').then(function(r){return r.json();}).then(function(d){
    document.getElementById('nivelNum').textContent=d.nivel.toFixed(1);
    document.getElementById('water').style.height=d.nivel.toFixed(0)+'%';
    document.getElementById('spLine').style.bottom=d.sp+'%';
    document.getElementById('spTag').textContent=d.sp;
    document.getElementById('spSlider').value=d.sp;
    document.getElementById('spNum').textContent=d.sp;
    document.getElementById('caudalVal').textContent=d.caudal.toFixed(2)+' L/min';

    var d1=document.getElementById('dot1');
    d1.className='dot '+(d.b1?'dot-on':'dot-off');
    var d2=document.getElementById('dot2');
    d2.className='dot '+(d.b2?'dot-on':'dot-off');

    document.getElementById('alarm').style.display=d.alarma?'block':'none';

    if(d.modo!==modoAuto){modoAuto=!!d.modo;refreshMode();}

    var ts=document.getElementById('ts');
    ts.textContent=new Date().toLocaleTimeString();
    ts.className='ok';
  }).catch(function(){
    var ts=document.getElementById('ts');
    ts.textContent='Sin conexion';
    ts.className='err';
  });
}

setInterval(poll,1000);
poll();
</script>
</body>
</html>
)HTMLEND";

// =============================================================================
// Estado recibido del Arduino
// =============================================================================
struct Sistema {
  float   nivel   = 0.0f;
  float   caudal  = 0.0f;
  bool    b1      = false;
  bool    b2      = false;
  uint8_t sp      = 80;
  bool    modo    = true;
  bool    alarma  = false;
  unsigned long ultimo_rx = 0;
} sys;

WebServer server(WEB_PORT);

// =============================================================================
// Parsear línea del Arduino: N:xx.x,Q:x.xx,B1:x,B2:x,SP:xx,M:x,A:x
// =============================================================================
static float extraerFloat(const String& s, const char* key) {
  int i = s.indexOf(key);
  return (i < 0) ? 0.0f : s.substring(i + strlen(key)).toFloat();
}
static int extraerInt(const String& s, const char* key) {
  int i = s.indexOf(key);
  return (i < 0) ? 0 : s.substring(i + strlen(key)).toInt();
}

void parsearSerial(const String& linea) {
  sys.nivel  = extraerFloat(linea, "N:");
  sys.caudal = extraerFloat(linea, "Q:");
  sys.b1     = extraerInt(linea, "B1:") == 1;
  sys.b2     = extraerInt(linea, "B2:") == 1;
  sys.sp     = (uint8_t)extraerInt(linea, "SP:");
  sys.modo   = extraerInt(linea, "M:") == 1;
  sys.alarma = extraerInt(linea, "A:") == 1;
  sys.ultimo_rx = millis();
}

// =============================================================================
// Handlers HTTP
// =============================================================================
void handleRoot() {
  server.send_P(200, "text/html", HTML_APP);
}

void handleData() {
  bool conectado = (millis() - sys.ultimo_rx) < TIMEOUT_ARDUINO_MS;
  char buf[160];
  snprintf(buf, sizeof(buf),
    "{\"nivel\":%.1f,\"caudal\":%.2f,\"b1\":%d,\"b2\":%d,"
    "\"sp\":%d,\"modo\":%d,\"alarma\":%d,\"conexion\":%d}",
    sys.nivel, sys.caudal,
    sys.b1 ? 1 : 0, sys.b2 ? 1 : 0,
    sys.sp, sys.modo ? 1 : 0,
    sys.alarma ? 1 : 0,
    conectado ? 1 : 0);
  server.send(200, "application/json", buf);
}

// Parseo JSON mínimo sin dependencia de ArduinoJson
// Formato esperado: {"cmd":"XX","val":N}
void handleCommand() {
  if (server.method() != HTTP_POST || !server.hasArg("plain")) {
    server.send(400, "text/plain", "Bad Request");
    return;
  }

  String body = server.arg("plain");

  // Extraer "cmd" (valor entre comillas)
  int ci = body.indexOf("\"cmd\"");
  int vi = body.indexOf("\"val\"");
  if (ci < 0 || vi < 0) { server.send(400, "text/plain", "Parse error"); return; }

  int q1 = body.indexOf('"', ci + 5) + 1;
  int q2 = body.indexOf('"', q1);
  String cmdKey = body.substring(q1, q2);

  int colonV = body.indexOf(':', vi + 5);
  int endV   = body.indexOf('}', colonV);
  int val    = body.substring(colonV + 1, endV).toInt();

  // Reenviar al Arduino con el protocolo definido
  String msg = cmdKey + ":" + String(val) + "\n";
  Serial2.print(msg);

  server.send(200, "application/json", "{\"ok\":1}");
}

// =============================================================================
void setup() {
  Serial.begin(115200);
  Serial2.begin(UART2_BAUD, SERIAL_8N1, UART2_RX_PIN, UART2_TX_PIN);

  // Punto de acceso WiFi — sin internet requerido
  WiFi.softAP(WIFI_SSID, WIFI_PASS);
  Serial.print("AP: "); Serial.print(WIFI_SSID);
  Serial.print("  IP: "); Serial.println(WiFi.softAPIP());

  server.on("/",     HTTP_GET,  handleRoot);
  server.on("/data", HTTP_GET,  handleData);
  server.on("/cmd",  HTTP_POST, handleCommand);
  server.begin();
  Serial.println("Servidor web listo.");
}

// =============================================================================
void loop() {
  server.handleClient();

  if (Serial2.available()) {
    String linea = Serial2.readStringUntil('\n');
    linea.trim();
    if (linea.length() > 4) parsearSerial(linea);
  }
}
