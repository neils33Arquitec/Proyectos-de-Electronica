% simulacion_sistema_llenado.m
% Sistema de llenado de flujo continuo — modelo SISO y espacio de estados
% Universidad Santiago Mariño — Teoría Moderna de Control
% Actualizado: Sesión 002 (v2 con sensor de nivel HC-SR04)
%
% INSTRUCCIONES:
%   1. Actualizar K, tau_q, L y A_tank con valores medidos experimentalmente.
%   2. Ejecutar sección por sección (Ctrl+Enter en cada bloque).

clear; clc; close all;

%% ── Parámetros del modelo ────────────────────────────────────────────────────
% Actualizar con identificación experimental
K      = 2.5;    % Ganancia estática bomba [L/min]
tau_q  = 3.0;    % Constante de tiempo bomba+tubería [s]
L      = 0.8;    % Retardo de transporte [s]
A_tank = 0.5;    % Área del tanque [L/cm]  (volumen/altura)

fprintf('=== Parámetros del Sistema ===\n');
fprintf('K = %.2f L/min  |  tau_q = %.2f s  |  L = %.2f s  |  A = %.2f L/cm\n\n', K, tau_q, L, A_tank);

%% ── Funciones de transferencia ───────────────────────────────────────────────
% Bomba + tubería (sin retardo)
G_bomba = tf([K], [tau_q, 1]);

% Tanque (integrador)
G_tanque = tf([1/A_tank], [1, 0]);

% Planta completa: bomba → tanque (sin retardo)
G_planta = series(G_bomba, G_tanque);

fprintf('G_bomba(s):\n'); G_bomba
fprintf('G_tanque(s):\n'); G_tanque
fprintf('G_planta(s) = G_bomba × G_tanque:\n'); G_planta

%% ── Espacio de estados ───────────────────────────────────────────────────────
A = [0,        1/A_tank;
     0,       -1/tau_q ];
B = [0;    K/tau_q];
C = eye(2);
D = zeros(2, 1);
sys_ss = ss(A, B, C, D);

fprintf('=== Espacio de Estados ===\n');
sys_ss

%% ── Controlabilidad y observabilidad ─────────────────────────────────────────
Mc = ctrb(sys_ss);
Mo = obsv(sys_ss);
fprintf('Rango Mc = %d (sistema %s)\n', rank(Mc), ternario(rank(Mc)==2,'CONTROLABLE','NO controlable'));
fprintf('Rango Mo = %d (sistema %s)\n\n', rank(Mo), ternario(rank(Mo)==2,'OBSERVABLE','NO observable'));

%% ── Respuesta al escalón — lazo abierto ─────────────────────────────────────
t = 0:0.05:60;
figure('Name','Respuesta al escalón — Lazo abierto');
subplot(2,1,1);
[y1, t1] = step(G_bomba, t);
plot(t1, y1, 'b-', 'LineWidth', 1.5); grid on;
title('Caudal q(t) — respuesta al escalón'); xlabel('t (s)'); ylabel('q (L/min)');

subplot(2,1,2);
[y2, t2] = step(G_planta, t);
plot(t2, y2, 'r-', 'LineWidth', 1.5); grid on;
title('Nivel h(t) — respuesta al escalón'); xlabel('t (s)'); ylabel('h (cm)');

%% ── Diagramas de Bode ────────────────────────────────────────────────────────
figure('Name','Bode');
bode(G_bomba, G_planta); grid on;
legend('G_{bomba}(s)', 'G_{planta}(s)', 'Location','best');
title('Diagrama de Bode');

%% ── Lugar geométrico de las raíces ──────────────────────────────────────────
figure('Name','Lugar de las raíces');
rlocus(G_planta); grid on;
title('Lugar Geométrico de las Raíces — G_{planta}(s)');

%% ── Diseño LQR (control óptimo) ──────────────────────────────────────────────
% Ponderación: penaliza más el error de nivel (estado 1) que el caudal
Q_lqr = diag([10, 1]);   % matriz de pesos de estados
R_lqr = 1;               % peso de la entrada de control

K_lqr = lqr(A, B, Q_lqr, R_lqr);
fprintf('=== Ganancias LQR ===\n');
fprintf('K_lqr = [%.4f, %.4f]\n\n', K_lqr(1), K_lqr(2));

% Sistema en lazo cerrado con LQR
A_lc = A - B * K_lqr;
sys_lc = ss(A_lc, B, C, D);

fprintf('Polos en lazo cerrado:\n');
disp(eig(A_lc));

%% ── Respuesta LQR vs lazo abierto ───────────────────────────────────────────
% Factor de precompensación para seguimiento (nivel de referencia = 80%)
N_bar = -1 / (C(1,:) * inv(A_lc) * B);

figure('Name','Lazo cerrado LQR');
t_lc = 0:0.05:30;
r_nivel = 80 * ones(size(t_lc));   % referencia 80%

% Simulación con lsim
[y_lc, ~] = lsim(sys_lc, N_bar * r_nivel, t_lc, [0; 0]);
subplot(2,1,1);
plot(t_lc, y_lc(:,1), 'b', t_lc, r_nivel, 'r--', 'LineWidth', 1.5); grid on;
title('Nivel h(t) — LQR'); xlabel('t (s)'); ylabel('Nivel (%)');
legend('h(t)', 'Referencia', 'Location','best');

subplot(2,1,2);
plot(t_lc, y_lc(:,2), 'g', 'LineWidth', 1.5); grid on;
title('Caudal q(t) — LQR'); xlabel('t (s)'); ylabel('q (L/min)');

%% ── Función auxiliar ─────────────────────────────────────────────────────────
function s = ternario(cond, a, b)
  if cond; s = a; else; s = b; end
end
