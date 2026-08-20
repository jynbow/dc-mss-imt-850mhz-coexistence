# Estudio DC-MSS-IMT — Coexistencia en la banda de 850 MHz

Simulaciones de compatibilidad espectral entre la constelación LEO Direct-to-Cell
de AST SpaceMobile (DC-MSS-IMT) y redes IMT terrestres, en la frontera
Colombia-Brasil (Leticia/Tabatinga). Escuela Colombiana de Ingeniería Julio
Garavito — curso Medios de Transmisión.

## Estructura del repositorio

```
.
├── 00_calculos_teoricos_originales/   Los 7 CSV de la cadena de calculo original
│   ├── 01_link_budget_imt_resultados.csv       (numeral 1 -- ver nota de C abajo)
│   ├── 02_slant_range_resultados.csv           (numeral 2, geometria)
│   ├── 03_fspl_satelite_resultados.csv         (numeral 2, FSPL)
│   ├── 04_ganancia_satelite_resultados.csv     (numeral 2, Gt lineal corregido)
│   ├── 05_potencia_interferente_resultados.csv (numeral 2-3, I teorico -- coincide EXACTO con Tabla 2)
│   ├── 06_barrido_potencia_resultados.csv      (numeral 5, 135 filas teoricas)
│   └── 07_criterios_interferencia_resultados.csv (numeral 4, criterios con C=-50.923 3GPP UMa manual)
│
├── 01_Python_Simulacion/              Scripts que corren el motor real de SHARC
│   ├── 00_link_budget_imt_uma_sharc.py         (numeral 1, con PropagationUMa real -- ver hallazgo abajo)
│   ├── A_barrido_potencia_10deg_p619.py
│   ├── B_barrido_angulo_potencia_p619.py
│   └── C_barrido_angular_fino_p619.py
│
├── 03_MATLAB_Graficas/                Scripts que leen los .csv y generan las graficas
│   ├── plot_A_barrido_potencia_10deg.m
│   ├── plot_B_matriz_angulo_potencia.m
│   └── plot_C_barrido_angular_fino.m
│
├── resultados_csv/                    Resultados REALES ya generados (no placeholders)
│   ├── A_barrido_potencia_10deg_SHARC.csv       (15 filas, C=-74.30 no aplica -- solo I/N)
│   ├── B_barrido_angulo_potencia_SHARC.csv      (135 filas, C=-74.30, igual que Tabla 2)
│   ├── C_barrido_angular_fino_SHARC.csv         (33 filas, C=-74.30)
│   ├── B_barrido_angulo_potencia_SHARC_C65.csv  (135 filas, C=-65.03, Parte 2)
│   └── C_barrido_angular_fino_SHARC_C65.csv     (33 filas, C=-65.03, Parte 2)
│
├── graficas_generadas/                Graficas ya generadas (PDF/PNG)
│   ├── Barrido_Potencia_4_Criterios_SHARC_REAL.pdf   (Parte 1, C=-74.30)
│   ├── Barrido_Potencia_4_Criterios_PARTE2_C65.pdf   (Parte 2, C=-65.03)
│   ├── Figura7_Tabla3_actualizada_SHARC_real.png
│   └── C_barrido_angular_fino_SHARC_real.png
│
└── TUTORIAL.pdf                       Instalacion desde cero (Python+SHARC, MATLAB)
```

## Hallazgo — Numeral 1, Link Budget IMT, con SHARC real (`00_link_budget_imt_uma_sharc.py`)

El script original (`01_link_budget_imt_resultados.csv`) calculó C a mano con
una aproximación de 3GPP UMa **LOS** (línea de vista despejada), dando
**-50.923 dBm**. Al correr el modelo `PropagationUMa` real de SHARC para el
mismo enlace (BS→UE, 3.5 km, 886.5 MHz), el resultado fue **NLOS** (sin línea
de vista), coincidiendo *exacto* con el valor NLOS ya calculado a mano
(150.996 dB de pérdida en ambos casos) — validando la fórmula, pero sugiriendo
que la premisa LOS del script original no era la físicamente correcta para
esta distancia.

> **Nota técnica:** `PropagationUMa.get_loss()` tiene un bug conocido con
> arrays de una sola estación (el mismo "SINGLE_BS edge case" ya documentado
> en este proyecto) — el script usa una matriz 2×2 con valores duplicados
> como workaround, y toma el resultado de la celda `[0,0]`.

### Comparativa de las 4 fuentes para C (numeral 1)

| Fuente | Modelo | C (dBm) |
|---|---|---|
| Referencia profesor | — (dato de entrada) | **-74.30** |
| SEAMCAT | P.1546 (o el configurado en el escenario) | -65.03 |
| Script `01` original | 3GPP UMa manual, asumiendo LOS | -50.923 |
| `00_link_budget_imt_uma_sharc.py` | 3GPP UMa real (SHARC), resultó NLOS | -87.996 |

**Decisión del equipo:** Parte 1 usa -74.30 (ya entregada). Parte 2 adopta
-65.03 (SEAMCAT) como C de referencia para el análisis de barrido de potencia,
por ser un valor simulado (no una aproximación manual con modelo sustituto).

## Los 3 scripts de simulación del barrido (Python)

| Script | Qué barre | Fijo | Filas | Motor |
|---|---|---|---|---|
| `A_barrido_potencia_10deg_p619.py` | Potencia Tx del satélite: 43→1 dBm (paso 3) | θ = 10° | 15 | `PropagationP619` real |
| `B_barrido_angulo_potencia_p619.py` | 9 ángulos oficiales × 15 potencias | — | 135 | `PropagationP619` real (9 llamadas reales, resto aritmética en dB) |
| `C_barrido_angular_fino_p619.py` | Ángulo: 10°→90°, paso 2.5° | Ptx = 43 dBm | 33 | `PropagationP619` real |

Los 3 usan la misma fórmula de ganancia de antena satelital corregida y
validada contra la Tabla 2 del informe (error 0.00 dB en los 9 puntos
oficiales):

$$G_t(\theta) = 30 - 0.375\,(\theta - 10) \quad \text{dBi}$$

> ⚠️ **Frecuencia — no mezclar:** `A` y `C` usan 886.5 MHz (proyecto METX,
> curso). `B` usa 887.75 MHz (proyecto de investigación, CMR-27 AI 1.13).

## Cómo correr todo (resumen)

**1. Simulación (Python + SHARC):**
```bash
cd SHARC/sharc
python 00_link_budget_imt_uma_sharc.py
python A_barrido_potencia_10deg_p619.py
python B_barrido_angulo_potencia_p619.py
python C_barrido_angular_fino_p619.py
```

**2. Gráficas (MATLAB):**
Copiar los `.csv` generados a `resultados_csv/`, abrir cada `.m` de
`03_MATLAB_Graficas/` en MATLAB y correr con F5. Las imágenes quedan en
`graficas_generadas/`.

Instrucciones completas paso a paso están en [`TUTORIAL.pdf`](./TUTORIAL.pdf).

## Validación cruzada — resumen de lo confirmado

- **A** (θ=10°, 43 dBm): `I_SHARC = -90.278 dBm` — coincide exacto con la Tabla 2.
- **B** (θ=10°, 43 dBm): pérdida atmosférica `0.1689 dB` — coincide exacto con
  la columna de error de la Tabla 2 en los 9 ángulos.
- **C** — cruces de umbral (con C=-74.30, Parte 1):
  - I/N ≤ -6 dB → θ ≈ 77.23° (no depende de C, igual en Parte 2)
  - C/I ≥ 19 dB → θ ≈ 35.41° (Parte 1) / nunca falla con C=-65.03 (Parte 2)
  - SINR ≥ 16 dB → θ ≈ 20.09° (Parte 1) / nunca falla con C=-65.03 (Parte 2)
  - I/(N+I) ≤ 0.97 dB → nunca falla en ninguno de los dos casos

## Créditos

Integrantes: Juan David Nova Gámez, John Alejandro Martínez González, Maikol
Julián Pulido Bautista. Profesor: Hernán Paz Penagos.

Motor de propagación: [SHARC](https://github.com/Radio-Spectrum/SHARC)
(Radio-Spectrum), implementando ITU-R P.619 (enlace satélite-Tierra) y el
modelo UMa (enlace terrestre BS-UE).
