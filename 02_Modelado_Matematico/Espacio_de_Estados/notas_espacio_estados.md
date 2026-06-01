# Representación en Espacio de Estados

## Variables del sistema (v2)

| Variable | Símbolo | Descripción                          | Unidad  |
|----------|---------|--------------------------------------|---------|
| Estado 1 | x₁ = h  | Nivel del tanque                     | %       |
| Estado 2 | x₂ = q  | Caudal de entrada (medido por GFS401)| L/min   |
| Entrada  | u       | Señal de control Bomba 1 (0 ó 1)    | —       |
| Salida 1 | y₁ = h  | Nivel (medido por HC-SR04)           | %       |
| Salida 2 | y₂ = q  | Caudal (medido por GFS401)           | L/min   |

---

## Ecuaciones de estado linealizadas

```
ẋ₁ =  (1/A) · x₂             ← nivel integra el caudal
ẋ₂ = -(1/τ_q)·x₂ + (K/τ_q)·u  ← dinámica de la bomba+tubería
```

### Forma matricial

```
⎡ẋ₁⎤   ⎡ 0      1/A  ⎤ ⎡x₁⎤   ⎡  0  ⎤
⎢  ⎥ = ⎢             ⎥·⎢  ⎥ + ⎢     ⎥·u
⎣ẋ₂⎦   ⎣ 0    -1/τ_q ⎦ ⎣x₂⎦   ⎣K/τ_q⎦

⎡y₁⎤   ⎡1  0⎤ ⎡x₁⎤   ⎡0⎤
⎢  ⎥ = ⎢    ⎥·⎢  ⎥ + ⎢ ⎥·u
⎣y₂⎦   ⎣0  1⎦ ⎣x₂⎦   ⎣0⎦
```

Matrices explícitas:

```
A = ⎡ 0      1/A  ⎤    B = ⎡  0  ⎤    C = ⎡1 0⎤    D = ⎡0⎤
    ⎣ 0    -1/τ_q ⎦        ⎣K/τ_q⎦        ⎣0 1⎦        ⎣0⎦
```

---

## Análisis de controlabilidad

Matriz de controlabilidad:

```
Mc = [B | A·B]

   = ⎡   0      K/(A·τ_q)  ⎤
     ⎣ K/τ_q  -K/τ_q²      ⎦
```

det(Mc) = -K²/τ_q² ≠ 0 siempre que **K ≠ 0**  
→ **Sistema completamente controlable** ✓

---

## Análisis de observabilidad

Matriz de observabilidad (con C = I₂):

```
Mo = ⎡  C  ⎤ = ⎡1  0⎤     → det(Mo) = 1 ≠ 0
     ⎣ C·A ⎦   ⎣0  1/A⎦
                ⎣0 -1/τ_q⎦
```

**Sistema completamente observable** ✓ (ambos estados medidos directamente)

---

## Valores numéricos (completar tras identificación)

```matlab
% MATLAB — ingresar tras identificación experimental
A_tank = ?;      % Área del tanque [L/cm]
K      = ?;      % Ganancia bomba
tau_q  = ?;      % Constante de tiempo [s]

A = [0,       1/A_tank;
     0,      -1/tau_q ];
B = [0;  K/tau_q];
C = eye(2);
D = zeros(2,1);
sys = ss(A, B, C, D);
```

---

## Polos del sistema

Valores propios de A:
- λ₁ = 0    (integrador del tanque — polo en el origen)
- λ₂ = -1/τ_q  (polo estable de la bomba)

El integrador garantiza **error nulo en régimen permanente** para referencia escalón de nivel.

---

## Diseño de controlador por realimentación de estados (propuesta)

Con los dos estados medibles (nivel y caudal), es posible diseñar un controlador por:

1. **Asignación de polos** — colocar polos en lazo cerrado en ubicaciones deseadas.
2. **LQR (Linear Quadratic Regulator)** — minimizar J = ∫(x'Qx + u'Ru)dt.

Matriz de ganancias K_c tal que:  
`u = -K_c·x + N·r`   donde N es el factor de precompensación para seguimiento.
