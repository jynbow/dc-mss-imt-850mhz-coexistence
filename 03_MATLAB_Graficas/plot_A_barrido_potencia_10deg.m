%% plot_A_barrido_potencia_10deg.m
% ============================================================
% Grafica los resultados del Script A (barrido de potencia, 10 grados
% fijo, METX numerales 5-7): Figura equivalente a la Figura 7 del informe.
%
% ENTRADA:  ../02_Resultados_CSV/A_barrido_potencia_10deg_SHARC.csv
% SALIDA:   ../04_Graficas_Generadas/A_barrido_potencia_10deg.png
%
% Como usar: abrir este archivo en MATLAB y presionar "Run" (F5).
% No hace falta cambiar nada si respetaste la estructura de carpetas
% del ZIP.
% ============================================================

clear; clc; close all;

carpeta_datos  = fullfile('..', '02_Resultados_CSV');
carpeta_salida = fullfile('..', '04_Graficas_Generadas');
if ~exist(carpeta_salida, 'dir')
    mkdir(carpeta_salida);
end

archivo = fullfile(carpeta_datos, 'A_barrido_potencia_10deg_SHARC.csv');
if ~exist(archivo, 'file')
    error(['No se encontro el archivo: ' archivo newline ...
           'Corre primero A_barrido_potencia_10deg_p619.py en Python ' ...
           'y copia el CSV generado a la carpeta 02_Resultados_CSV.']);
end

T = readtable(archivo);

ptx      = T.ptx_sat_dbm;
I_teor   = T.I_teorico_dbm;
I_sharc  = T.I_SHARC_P619_dbm;
IN_teor  = T.IN_teorico_db;
IN_sharc = T.IN_SHARC_db;

N_DBM = -99.00;
LIM_OK     = -6.0;
LIM_ALERTA = -3.0;

figure('Position', [100 100 1200 500], 'Color', 'w');

% ---- Subplot 1: Potencia interferente I vs Ptx ----
subplot(1,2,1);
plot(ptx, I_teor, '-o', 'LineWidth', 1.8, 'Color', [0.2 0.3 0.6], ...
     'DisplayName', 'Teorico'); hold on;
plot(ptx, I_sharc, '--s', 'LineWidth', 1.8, 'Color', [0.75 0.2 0.2], ...
     'DisplayName', 'Simulado (SHARC P.619)');
xlabel('Potencia Tx satelite (dBm)');
ylabel('I (dBm)');
title('Potencia interferente vs. potencia transmitida (\theta = 10^\circ)');
legend('Location', 'northwest');
grid on;
set(gca, 'XDir', 'reverse');   % igual que el informe: 43 -> 1 dBm

% ---- Subplot 2: I/N vs Ptx, con zonas de cumplimiento ----
subplot(1,2,2);
yl = [min(IN_sharc)-3, max(IN_sharc)+3];
xl = [min(ptx)-2, max(ptx)+2];

% fondo de zonas (rojo=cancelable, amarillo=alerta, verde=aceptable)
patch([xl(1) xl(2) xl(2) xl(1)], [LIM_ALERTA LIM_ALERTA yl(2) yl(2)], ...
      [0.90 0.55 0.55], 'EdgeColor', 'none', 'FaceAlpha', 0.35); hold on;
patch([xl(1) xl(2) xl(2) xl(1)], [LIM_OK LIM_OK LIM_ALERTA LIM_ALERTA], ...
      [0.95 0.85 0.45], 'EdgeColor', 'none', 'FaceAlpha', 0.35);
patch([xl(1) xl(2) xl(2) xl(1)], [yl(1) yl(1) LIM_OK LIM_OK], ...
      [0.55 0.80 0.55], 'EdgeColor', 'none', 'FaceAlpha', 0.35);

plot(ptx, IN_teor, '-o', 'LineWidth', 1.8, 'Color', [0.2 0.3 0.6], ...
     'DisplayName', 'Teorico');
plot(ptx, IN_sharc, '--s', 'LineWidth', 1.8, 'Color', [0.75 0.2 0.2], ...
     'DisplayName', 'Simulado (SHARC P.619)');
yline(LIM_OK, 'k--', 'LineWidth', 1.4, 'DisplayName', 'Umbral aceptable (-6 dB)');
yline(LIM_ALERTA, 'k:', 'LineWidth', 1.2, 'DisplayName', 'Umbral alerta (-3 dB)');

xlabel('Potencia Tx satelite (dBm)');
ylabel('I/N (dB)');
title('Criterio I/N \leq -6 dB vs. potencia (\theta = 10^\circ)');
legend('Location', 'northwest');
grid on;
xlim(xl); ylim(yl);
set(gca, 'XDir', 'reverse');

sgtitle(['Barrido de potencia, \theta = 10^\circ fijo (N = ' num2str(N_DBM) ' dBm constante)'], ...
        'FontWeight', 'bold', 'FontSize', 13);

archivo_salida = fullfile(carpeta_salida, 'A_barrido_potencia_10deg.png');
exportgraphics(gcf, archivo_salida, 'Resolution', 150);
fprintf('Grafica guardada en: %s\n', archivo_salida);
