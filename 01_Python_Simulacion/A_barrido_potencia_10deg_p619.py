"""
SCRIPT A -- Barrido de potencia a 10 grados fijo (METX, numerales 5-7)
========================================================================

Objetivo (numeral 5 de la guia): "potencia de transmision del satelite
variando de manera descendente de 3 en 3 desde su valor maximo 43 dBm,
cuando estan alineados a 10 grados de elevacion con su ganancia de
antena maxima [...] SLANT RANGE para 10 grados."

theta queda FIJO en 10 grados (ahi la formula lineal corregida da la
ganancia MAXIMA del satelite, Gt=30 dBi). Lo unico que cambia por fila
es P_TX_SAT_DBM: 43, 40, 37, ..., 1 dBm (15 niveles).

Motor de propagacion: el MISMO PropagationP619 real de tu instalacion
de SHARC que ya usaste para validar los 9 angulos oficiales de la
Tabla 2 del informe (error 0.00 dB contra el motor real).

Ejecutar DENTRO de sharc/, en tu venv de Python 3.12:
    cd C:\\Users\\john2\\Proyectos\\SHARC\\sharc
    python A_barrido_potencia_10deg_p619.py

Genera: A_barrido_potencia_10deg_SHARC.csv
"""

import sys, os, math, csv
import numpy as np

sys.path.insert(0, os.getcwd())
from sharc.propagation.propagation_p619 import PropagationP619  # noqa: E402

# ============================================================
# PARAMETROS -- identicos a los usados para validar la Tabla 2
# ============================================================
R_TIERRA_KM = 6371.0
ALTURA_SAT_KM = 510.0
FRECUENCIA_MHZ = 886.5           # proyecto METX. NO cambiar aqui salvo que
                                  # tambien cambies el resto del informe METX.
G_RX_UE_DBI = 2.0
PERDIDAS_TX_SAT_DB = 3.0
PERDIDAS_RX_UE_DB = 6.0
EARTH_STATION_ALT_M = 82.0
EARTH_STATION_LAT_DEG = -4.207736
SEASON = "SUMMER"

THETA_FIJO_DEG = 10.0
POTENCIAS_DBM = list(range(43, 0, -3))   # 43,40,...,1  (15 niveles)
N_DBM = -99.00


def slant_range_km(elevacion_deg):
    e = math.radians(elevacion_deg)
    return -R_TIERRA_KM * math.sin(e) + math.sqrt(
        (R_TIERRA_KM + ALTURA_SAT_KM) ** 2 - (R_TIERRA_KM * math.cos(e)) ** 2
    )


def ganancia_satelite_dbi(theta_deg):
    """Formula lineal corregida por el profesor. En 10 grados da 30 dBi (maxima)."""
    return 30.0 - 0.375 * (theta_deg - 10.0)


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

    slant = slant_range_km(THETA_FIJO_DEG)
    gt = ganancia_satelite_dbi(THETA_FIJO_DEG)
    fspl = 32.45 + 20 * math.log10(slant) + 20 * math.log10(FRECUENCIA_MHZ)
    perdida_atm = p619._get_atmospheric_gasses_loss(
        frequency_MHz=FRECUENCIA_MHZ, apparent_elevation=THETA_FIJO_DEG,
    )
    perdida_total = fspl + perdida_atm

    print(f"Theta fijo: {THETA_FIJO_DEG} deg | Slant: {slant:.2f} km | "
          f"Gt: {gt:.2f} dBi (debe ser 30.00) | FSPL: {fspl:.3f} dB | "
          f"Perdida atm P.619: {perdida_atm:.4f} dB\n")

    filas = []
    print(f"{'Ptx':>5} | {'I_teorico':>10} | {'I_SHARC':>10} | {'IN_teor':>8} | {'IN_SHARC':>9} | Cumple(SHARC)")
    for ptx in POTENCIAS_DBM:
        I_teorico = ptx + gt + G_RX_UE_DBI - PERDIDAS_TX_SAT_DB - PERDIDAS_RX_UE_DB - fspl
        I_sharc = ptx + gt + G_RX_UE_DBI - PERDIDAS_TX_SAT_DB - PERDIDAS_RX_UE_DB - perdida_total
        IN_teorico = I_teorico - N_DBM
        IN_sharc = I_sharc - N_DBM
        cumple = "OK" if IN_sharc <= -6.0 else "NO"
        filas.append([ptx, slant, fspl, gt, perdida_atm, I_teorico, I_sharc, IN_teorico, IN_sharc, cumple])
        print(f"{ptx:>5} | {I_teorico:>10.3f} | {I_sharc:>10.3f} | {IN_teorico:>8.3f} | {IN_sharc:>9.3f} | {cumple}")

    with open("A_barrido_potencia_10deg_SHARC.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["ptx_sat_dbm", "slant_km", "fspl_db", "gt_dbi", "perdida_atm_db",
                    "I_teorico_dbm", "I_SHARC_P619_dbm", "IN_teorico_db", "IN_SHARC_db", "cumple_SHARC"])
        w.writerows(filas)
    print("\nArchivo generado: A_barrido_potencia_10deg_SHARC.csv")


if __name__ == "__main__":
    main()
