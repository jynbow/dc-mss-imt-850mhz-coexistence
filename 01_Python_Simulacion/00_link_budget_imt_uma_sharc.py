"""
Numeral 1 -- Link Budget IMT (BS -> UE), con el modelo UMa REAL de SHARC
==========================================================================
VERSION 4 -- workaround del "SINGLE_BS edge case" (bug conocido de SHARC,
ya documentado en este mismo proyecto).

Causa raiz del IndexError de la version 3: dentro de get_loss_los(), la
linea

    fitting_term = -10 * np.log10(
        breakpoint_distance**2 + (h_bs - h_ue[:, np.newaxis])**2,
    )

fuerza a h_ue a comportarse como columna de una matriz de VARIAS filas.
Con un solo UE (array de longitud 1), el broadcasting resultante desalinea
las formas y rompe el indexado un par de lineas despues, en
distance_3D[idg].

WORKAROUND: en vez de simular 1 BS x 1 UE, simulamos una matriz 2x2 (2
BS x 2 UE) con el MISMO valor duplicado en ambas filas/columnas -- eso
evita el camino de codigo que falla con arrays de longitud 1. El
resultado real esta en cualquiera de las 4 celdas (todas identicas, ya
que los valores de entrada son iguales); tomamos [0, 0].

Ejecutar DENTRO de sharc/, en el venv:
    cd C:\\Users\\john2\\Proyectos\\SHARC\\sharc
    python 00_link_budget_imt_uma_sharc.py
"""

import sys
import os
import math
import numpy as np

sys.path.insert(0, os.getcwd())

from sharc.propagation.propagation_uma import PropagationUMa  # noqa: E402

# ============================================================
# PARAMETROS (identicos al resto del proyecto / YAML oficial)
# ============================================================
DISTANCIA_2D_M = 3500.0
FRECUENCIA_MHZ = 886.5
ALTURA_BS_M = 25.0
ALTURA_UE_M = 1.5
P_TX_BS_DBM = 46.0
G_BS_DBI = 15.0
G_UE_DBI = 2.0

DISTANCIA_3D_M = math.sqrt(DISTANCIA_2D_M**2 + (ALTURA_BS_M - ALTURA_UE_M)**2)


def calcular(shadowing_activado: bool, prop: PropagationUMa):
    # Matrices 2x2 (2 BS "fantasma" x 2 UE "fantasma"), todo duplicado --
    # workaround del SINGLE_BS edge case. El resultado real esta repetido
    # identico en las 4 celdas.
    distance_3d = np.full((2, 2), DISTANCIA_3D_M)
    distance_2d = np.full((2, 2), DISTANCIA_2D_M)
    frequency   = np.full((2, 2), FRECUENCIA_MHZ)
    bs_height   = np.array([ALTURA_BS_M, ALTURA_BS_M])
    ue_height   = np.array([ALTURA_UE_M, ALTURA_UE_M])

    perdida = prop.get_loss(
        distance_3d,
        distance_2d,
        frequency,
        bs_height,
        ue_height,
        shadowing_activado,
    )
    perdida = np.asarray(perdida)
    print(f"    (matriz de perdidas 2x2 resultante: {perdida.tolist()})")
    return float(perdida[0, 0])


def main():
    rng = np.random.RandomState(1)
    prop = PropagationUMa(random_number_gen=rng)

    print(f"Distancia 2D: {DISTANCIA_2D_M} m | Distancia 3D: {DISTANCIA_3D_M:.3f} m")
    print(f"Frecuencia: {FRECUENCIA_MHZ} MHz\n")

    print("Calculando SIN shadowing...")
    perdida_sin_sh = calcular(False, prop)
    c_sin_sh = P_TX_BS_DBM + G_BS_DBI + G_UE_DBI - perdida_sin_sh

    print(f"\n{'='*55}")
    print(f"SIN shadowing (comparable con el resto del proyecto):")
    print(f"  Perdida UMa (SHARC): {perdida_sin_sh:.3f} dB")
    print(f"  C (DRSS teorico):    {c_sin_sh:.3f} dBm")
    print(f"{'='*55}")

    try:
        print("\nCalculando CON shadowing...")
        perdida_con_sh = calcular(True, prop)
        c_con_sh = P_TX_BS_DBM + G_BS_DBI + G_UE_DBI - perdida_con_sh
        print(f"\nCON shadowing (informativo, con componente aleatorio):")
        print(f"  Perdida UMa (SHARC): {perdida_con_sh:.3f} dB")
        print(f"  C (DRSS):            {c_con_sh:.3f} dBm")
    except Exception as e:
        print(f"\n(No se pudo calcular con shadowing: {type(e).__name__}: {e})")

    print(f"\n{'='*55}")
    print("COMPARATIVA COMPLETA -- Numeral 1 (C, DRSS teorico)")
    print(f"{'='*55}")
    print(f"  Referencia profesor:          -74.30 dBm")
    print(f"  SEAMCAT (evidencia real):     -65.03 dBm")
    print(f"  3GPP UMa manual (script 01):  -50.923 dBm")
    print(f"  SHARC UMa, sin shadowing:     {c_sin_sh:.3f} dBm")


if __name__ == "__main__":
    main()
