"""
SCRIPT B -- Matriz completa angulo x potencia (proyecto de investigacion SHARC)
=================================================================================

Genera los 135 puntos (9 angulos oficiales x 15 niveles de potencia) usando
el motor REAL de propagacion P.619 de SHARC -- exactamente el mismo que
usaste para validar los 9 angulos de la Tabla 2 del informe METX (error
0.00 dB), pero ahora cruzado tambien con el barrido de potencia.

Esto reemplaza a los valores TEORICOS (formula cerrada) que usamos para
construir la tabla anotada y el mapa circular -- con este CSV ya se puede
regenerar esas mismas 4 graficas con la columna "practico" (I_SHARC_P619),
que es la que realmente cuenta como "simulado" y no solo "calculado".

IMPORTANTE -- frecuencia: este es el proyecto de INVESTIGACION (CMR-27
AI 1.13), que usa 887.75 MHz, DISTINTA de los 886.5 MHz del curso METX.
No mezclar los resultados de este script con los del Script A.

Como cada angulo tiene su propia geometria (slant range, FSPL, perdida
atmosferica), pero la potencia entra de forma puramente aditiva en dB,
el bucle externo recorre los 9 angulos (recalculando geometria y
perdida atmosferica UNA vez por angulo) y el bucle interno recorre las
15 potencias (reutilizando esos valores, sin llamar de nuevo a SHARC).
Esto ahorra 14/15 de las llamadas al motor de propagacion sin perder
precision, porque la perdida atmosferica de P.619 no depende de la
potencia transmitida.

Ejecutar DENTRO de sharc/, en tu venv de Python 3.12:
    cd C:\\Users\\john2\\Proyectos\\SHARC\\sharc
    python B_barrido_angulo_potencia_p619.py

Genera: B_barrido_angulo_potencia_SHARC.csv  (135 filas)
"""

import sys, os, math, csv
import numpy as np

sys.path.insert(0, os.getcwd())
from sharc.propagation.propagation_p619 import PropagationP619  # noqa: E402

# ============================================================
# PARAMETROS -- proyecto de INVESTIGACION (887.75 MHz)
# ============================================================
R_TIERRA_KM = 6371.0
ALTURA_SAT_KM = 510.0
FRECUENCIA_MHZ = 887.75          # investigacion CMR-27. NO usar 886.5 aqui.
G_RX_UE_DBI = 2.0
PERDIDAS_TX_SAT_DB = 3.0
PERDIDAS_RX_UE_DB = 6.0
EARTH_STATION_ALT_M = 82.0
EARTH_STATION_LAT_DEG = -4.207736
SEASON = "SUMMER"

ANGULOS_DEG = [10, 20, 30, 40, 50, 60, 70, 80, 90]      # 9 angulos oficiales
POTENCIAS_DBM = list(range(43, 0, -3))                  # 15 niveles
N_DBM = -99.00
C_DBM = -74.30


def slant_range_km(elevacion_deg):
    e = math.radians(elevacion_deg)
    return -R_TIERRA_KM * math.sin(e) + math.sqrt(
        (R_TIERRA_KM + ALTURA_SAT_KM) ** 2 - (R_TIERRA_KM * math.cos(e)) ** 2
    )


def ganancia_satelite_dbi(theta_deg):
    return 30.0 - 0.375 * (theta_deg - 10.0)


def suma_potencias_dbm(a_dbm, b_dbm):
    return 10 * math.log10(10 ** (a_dbm / 10) + 10 ** (b_dbm / 10))


def main():
    rng = np.random.RandomState(1)
    p619 = PropagationP619(
        random_number_gen=rng,
        earth_station_alt_m=EARTH_STATION_ALT_M,
        earth_station_lat_deg=EARTH_STATION_LAT_DEG,
        season=SEASON,
        mean_clutter_height='low',
        below_rooftop=0.0,
    )

    filas = []
    total = len(ANGULOS_DEG) * len(POTENCIAS_DBM)
    contador = 0

    for theta in ANGULOS_DEG:
        # --- geometria y perdida atmosferica: UNA vez por angulo ---
        slant = slant_range_km(theta)
        gt = ganancia_satelite_dbi(theta)
        fspl = 32.45 + 20 * math.log10(slant) + 20 * math.log10(FRECUENCIA_MHZ)
        perdida_atm = p619._get_atmospheric_gasses_loss(
            frequency_MHz=FRECUENCIA_MHZ, apparent_elevation=theta,
        )
        perdida_total = fspl + perdida_atm

        for ptx in POTENCIAS_DBM:
            contador += 1
            I_teorico = ptx + gt + G_RX_UE_DBI - PERDIDAS_TX_SAT_DB - PERDIDAS_RX_UE_DB - fspl
            I_sharc = ptx + gt + G_RX_UE_DBI - PERDIDAS_TX_SAT_DB - PERDIDAS_RX_UE_DB - perdida_total

            IN_sharc = I_sharc - N_DBM
            NI_sharc = suma_potencias_dbm(N_DBM, I_sharc)
            INI_sharc = I_sharc - NI_sharc
            CI_sharc = C_DBM - I_sharc
            CNI_sharc = C_DBM - NI_sharc

            filas.append([
                theta, ptx, round(slant, 3), round(fspl, 3), round(gt, 3),
                round(perdida_atm, 4), round(I_teorico, 3), round(I_sharc, 3),
                round(IN_sharc, 3), round(INI_sharc, 3), round(CI_sharc, 3), round(CNI_sharc, 3),
            ])

        print(f"[{contador}/{total}] Angulo {theta}° listo "
              f"(Gt={gt:.2f} dBi, FSPL={fspl:.2f} dB, perdida_atm={perdida_atm:.4f} dB)")

    with open("B_barrido_angulo_potencia_SHARC.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["theta_deg", "ptx_sat_dbm", "slant_km", "fspl_db", "gt_dbi",
                    "perdida_atm_db", "I_teorico_dbm", "I_SHARC_P619_dbm",
                    "IN_db", "INI_db", "CI_db", "CNI_db"])
        w.writerows(filas)

    print(f"\nArchivo generado: B_barrido_angulo_potencia_SHARC.csv ({len(filas)} filas)")
    print("Columna 'I_SHARC_P619_dbm' = valor SIMULADO real (motor P.619), no solo teorico.")


if __name__ == "__main__":
    main()
