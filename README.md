# Estudio DC-MSS-IMT — Coexistencia en la banda de 850 MHz

Simulaciones de compatibilidad espectral entre la constelación LEO Direct-to-Cell
de AST SpaceMobile (DC-MSS-IMT) y redes IMT terrestres, en la frontera
Colombia-Brasil (Leticia/Tabatinga). Escuela Colombiana de Ingeniería Julio
Garavito — curso Medios de Transmisión.

Este repositorio contiene los scripts de **simulación** (Python, motor real
`PropagationP619` de [SHARC](https://github.com/Radio-Spectrum/SHARC)) y de
**visualización** (MATLAB) del barrido de potencia y del análisis conjunto
ángulo×potencia, complementarios al análisis de 9 ángulos oficiales del informe
principal.

## Estructura del repositorio

```
.
├── 01_Python_Simulacion/       Scripts que corren el motor real de SHARC
│   ├── A_barrido_potencia_10deg_p619.py
│   ├── B_barrido_angulo_potencia_p619.py
│   └── C_barrido_angular_fino_p619.py
│
├── 03_MATLAB_Graficas/         Scripts que leen los .csv y generan las gráficas
│   ├── plot_A_barrido_potencia_10deg.m
│   ├── plot_B_matriz_angulo_potencia.m
│   └── plot_C_barrido_angular_fino.m
│
├── resultados_csv/             Salida de los scripts de Python (no versionada,
│                                ver .gitignore — cada quien genera la suya)
│
└── graficas_generadas/         Salida de los scripts de MATLAB (no versionada)
```

## Los 3 scripts de simulación (Python)

| Script | Qué barre | Fijo | Filas | Motor |
|---|---|---|---|---|
| `A_barrido_potencia_10deg_p619.py` | Potencia Tx del satélite: 43→1 dBm (paso 3) | θ = 10° | 15 | `PropagationP619` real |
| `B_barrido_angulo_potencia_p619.py` | 9 ángulos oficiales × 15 potencias | — | 135 | `PropagationP619` real (9 llamadas reales, resto aritmética en dB) |
| `C_barrido_angular_fino_p619.py` | Ángulo: 10°→90°, paso 2.5° | Ptx = 43 dBm | 33 | `PropagationP619` real |

Los 3 usan la misma fórmula de ganancia de antena satelital **corregida y
validada** contra la Tabla 2 del informe (error 0.00 dB en los 9 puntos
oficiales):

$$G_t(\theta) = 30 - 0.375\,(\theta - 10) \quad \text{dBi}$$

> ⚠️ **Frecuencia — no mezclar:** `A` y `C` usan 886.5 MHz (proyecto METX,
> curso). `B` usa 887.75 MHz (proyecto de investigación, CMR-27 AI 1.13). Está
> indicado en un comentario al inicio de cada script.

## Los 3 scripts de graficación (MATLAB)

| Script | Lee | Genera |
|---|---|---|
| `plot_A_barrido_potencia_10deg.m` | `A_..._SHARC.csv` | 1 imagen — I e I/N vs. potencia (equivalente a la Fig. 7 del informe) |
| `plot_B_matriz_angulo_potencia.m` | `B_..._SHARC.csv` | 4 imágenes — una por criterio (I/N, I/(N+I), C/I, SINR), cada una con tabla anotada + mapa circular + curvas |
| `plot_C_barrido_angular_fino.m` | `C_..._SHARC.csv` | 1 imagen — los 4 criterios, curva fina con los 9 puntos oficiales resaltados |

## Cómo correr todo (resumen)

**1. Simulación (Python + SHARC):**
```bash
# Requiere Python 3.12 exacto (3.10/11 fallan por f-strings, 3.13/14 por numpy)
cd SHARC/sharc
python A_barrido_potencia_10deg_p619.py
python B_barrido_angulo_potencia_p619.py
python C_barrido_angular_fino_p619.py
```
Cada uno genera su `.csv` en la misma carpeta.

**2. Gráficas (MATLAB):**
Copiar los `.csv` generados a `resultados_csv/`, abrir cada `.m` de
`03_MATLAB_Graficas/` en MATLAB y correr con F5. Las imágenes quedan en
`graficas_generadas/`.

Instrucciones completas paso a paso (instalación desde cero de Python, SHARC y
MATLAB) están en [`TUTORIAL.pdf`](./TUTORIAL.pdf).

## Validación

Los 3 scripts fueron corridos y sus resultados contrastados contra la Tabla 2
del informe oficial (9 ángulos, validados por el profesor):

- **A** (θ=10°, 43 dBm): `I_SHARC = -90.278 dBm` — coincide exacto con la Tabla 2.
- **B** (θ=10°, 43 dBm): pérdida atmosférica `0.1689 dB` — coincide exacto con
  la columna de error de la Tabla 2 en los 9 ángulos.
- **C**: cruces de umbral detectados por interpolación lineal:
  - I/N ≤ -6 dB → θ ≈ 77.23°
  - C/I ≥ 19 dB → θ ≈ 35.41°
  - SINR ≥ 16 dB → θ ≈ 20.09°
  - I/(N+I) ≤ 0.97 dB → nunca falla en 10°-90°

## Créditos

Integrantes: Juan David Nova Gámez, John Alejandro Martínez González, Maikol
Julián Pulido Bautista. Profesor: Hernán Paz Penagos.

Motor de propagación: [SHARC](https://github.com/Radio-Spectrum/SHARC)
(Radio-Spectrum), implementando ITU-R P.619.
