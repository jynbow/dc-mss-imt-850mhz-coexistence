"""
SCRIPT C -- Barrido angular FINO (paso 2.5 grados), potencia fija
====================================================================

Extiende el barrido angular oficial de 9 puntos (paso 10 grados, el que
valida la Tabla 2 del informe) a resolucion fina de 2.5 grados:

    ANGULOS_DEG = 10, 12.5, 15, 17.5, ..., 87.5, 90   -> 33 puntos

Mismo motor real (PropagationP619) y misma formula lineal corregida de
ganancia -- SOLO cambia la resolucion angular. Sirve para ver el
comportamiento de los 4 criterios entre los 9 puntos oficiales (por
ejemplo, exactamente en que angulo cruza cada umbral, no solo "entre
30 y 40 grados").

SUPUESTOS que puedes ajustar arriba en PARAMETROS:
  - PTX_FIJO_DBM = 43.0  (potencia maxima del satelite, la misma que usa
    la Tabla 2 del informe -- cambiar aqui si quieres otro nivel fijo)
  - FRECUENCIA_MHZ = 886.5  (proyecto METX; cambiar a 887.75 para el
    proyecto de investigacion -- NO MEZCLAR resultados de ambas)

Ejecutar DENTRO de sharc/, en tu venv de Python 3.12:
    cd C:\\Users\\john2\\Proyectos\\SHARC\\sharc
    python C_barrido_angular_fino_p619.py

Genera: C_barrido_angular_fino_SHARC.csv  (33 filas)

NOTA sobre visualizacion: si luego quieres el "mapa circular" con estos
33 puntos, ya NO aplica la convencion de "9 anillos, radio=50km/9" que
aprobo el profesor para el entregable oficial -- esa convencion es
especifica de la version de 9 angulos. Para 33 puntos habria que
redefinir el paso de radio (50km/33) o usar otro tipo de grafica
(por ejemplo, solo la vista cartesiana, sin la radial). Avisame si
llegas a ese punto y lo resolvemos.
"""

import sys, os, math, csv
import numpy as np

sys.path.insert(0, os.getcwd())
from sharc.propagation.propagation_p619 import PropagationP619  # noqa: E402

# ============================================================
# PARAMETROS
# ============================================================
R_TIERRA_KM = 6371.0
ALTURA_SAT_KM = 510.0
FRECUENCIA_MHZ = 886.5           # METX. Cambiar a 887.75 para investigacion.
PTX_FIJO_DBM = 43.0              # potencia fija (la misma que usa la Tabla 2)
G_RX_UE_DBI = 2.0
PERDIDAS_TX_SAT_DB = 3.0
PERDIDAS_RX_UE_DB = 6.0
EARTH_STATION_ALT_M = 82.0
EARTH_STATION_LAT_DEG = -4.207736
SEASON = "SUMMER"

PASO_DEG = 2.5
ANGULOS_DEG = np.arange(10.0, 90.0 + PASO_DEG / 2, PASO_DEG)  # 10, 12.5, ..., 90 -> 33 puntos

N_DBM = -99.00
C_DBM = -74.30


def slant_range_km(elevacion_deg):
    e = math.radians(elevacion_deg)
    return -R_TIERRA_KM * math.sin(e) + math.sqrt(
        (R_TIERRA_KM + ALTURA_SAT_KM) ** 2 - (R_TIERRA_KM * math.cos(e)) ** 2
    )


def ganancia_satelite_dbi(theta_deg):
    """Formula lineal corregida: 30 dBi en 10 grados, 0 dBi en 90 grados."""
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

    print(f"Potencia fija: {PTX_FIJO_DBM} dBm | Frecuencia: {FRECUENCIA_MHZ} MHz | "
          f"{len(ANGULOS_DEG)} angulos (paso {PASO_DEG}°)\n")

    filas = []
    print(f"{'theta':>6} | {'slant_km':>9} | {'Gt':>6} | {'I_SHARC':>9} | {'IN':>7} | {'CI':>7} | {'CNI':>7} | Cumple(IN)")
    for theta in ANGULOS_DEG:
        theta = round(float(theta), 2)
        slant = slant_range_km(theta)
        gt = ganancia_satelite_dbi(theta)
        fspl = 32.45 + 20 * math.log10(slant) + 20 * math.log10(FRECUENCIA_MHZ)
        perdida_atm = p619._get_atmospheric_gasses_loss(
            frequency_MHz=FRECUENCIA_MHZ, apparent_elevation=theta,
        )
        perdida_total = fspl + perdida_atm

        I_teorico = PTX_FIJO_DBM + gt + G_RX_UE_DBI - PERDIDAS_TX_SAT_DB - PERDIDAS_RX_UE_DB - fspl
        I_sharc = PTX_FIJO_DBM + gt + G_RX_UE_DBI - PERDIDAS_TX_SAT_DB - PERDIDAS_RX_UE_DB - perdida_total

        IN = I_sharc - N_DBM
        NI = suma_potencias_dbm(N_DBM, I_sharc)
        INI = I_sharc - NI
        CI = C_DBM - I_sharc
        CNI = C_DBM - NI
        cumple = "OK" if IN <= -6.0 else "NO"

        filas.append([theta, round(slant, 3), round(fspl, 3), round(gt, 3), round(perdida_atm, 4),
                      round(I_teorico, 3), round(I_sharc, 3), round(IN, 3), round(INI, 3),
                      round(CI, 3), round(CNI, 3), cumple])

        print(f"{theta:>6} | {slant:>9.2f} | {gt:>6.2f} | {I_sharc:>9.3f} | {IN:>7.3f} | "
              f"{CI:>7.3f} | {CNI:>7.3f} | {cumple}")

    with open("C_barrido_angular_fino_SHARC.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["theta_deg", "slant_km", "fspl_db", "gt_dbi", "perdida_atm_db",
                    "I_teorico_dbm", "I_SHARC_P619_dbm", "IN_db", "INI_db", "CI_db", "CNI_db",
                    "cumple_IN"])
        w.writerows(filas)

    # -- deteccion automatica del angulo exacto donde cruza cada umbral --
    print("\n--- Cruce de umbrales (interpolacion lineal entre puntos consecutivos) ---")
    umbrales = [("IN", -6.0, 7), ("INI", 0.97, 8), ("CI", 19.0, 9), ("CNI", 16.0, 10)]
    for nombre, lim, col in umbrales:
        for i in range(len(filas) - 1):
            v0, v1 = filas[i][col], filas[i + 1][col]
            th0, th1 = filas[i][0], filas[i + 1][0]
            if (v0 - lim) * (v1 - lim) < 0:  # cambia de signo -> cruza el umbral aqui
                theta_cruce = th0 + (lim - v0) * (th1 - th0) / (v1 - v0)
                print(f"  {nombre} cruza {lim} dB entre {th0}° y {th1}° "
                      f"-> aprox. en theta = {theta_cruce:.2f}°")

    print(f"\nArchivo generado: C_barrido_angular_fino_SHARC.csv ({len(filas)} filas)")


if __name__ == "__main__":
    main()
