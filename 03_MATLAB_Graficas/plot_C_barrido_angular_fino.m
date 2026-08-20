%% plot_C_barrido_angular_fino.m
% ============================================================
% Grafica los resultados del Script C (33 angulos, paso 2.5 grados,
% potencia fija). Genera una figura con los 4 criterios juntos
% (2x2), marcando ademas los 9 puntos angulares oficiales (10,20,...,90)
% sobre la curva fina para que se vea la relacion con la Tabla 2.
%
% ENTRADA:  ../02_Resultados_CSV/C_barrido_angular_fino_SHARC.csv
% SALIDA:   ../04_Graficas_Generadas/C_barrido_angular_fino.png
%
% Como usar: abrir en MATLAB y presionar "Run" (F5).
% ============================================================

clear; clc; close all;

carpeta_datos  = fullfile('..', '02_Resultados_CSV');
carpeta_salida = fullfile('..', '04_Graficas_Generadas');
if ~exist(carpeta_salida, 'dir')
    mkdir(carpeta_salida);
end

archivo = fullfile(carpeta_datos, 'C_barrido_angular_fino_SHARC.csv');
if ~exist(archivo, 'file')
    error(['No se encontro el archivo: ' archivo newline ...
           'Corre primero C_barrido_angular_fino_p619.py en Python ' ...
           'y copia el CSV generado a la carpeta 02_Resultados_CSV.']);
end

T = readtable(archivo);
theta = T.theta_deg;

criterios = struct( ...
    'columna',    {'IN_db',       'INI_db',            'CI_db',        'CNI_db'}, ...
    'titulo',     {'I/N \leq -6 dB', 'I/(N+I) \leq 0.97 dB', 'C/I \geq 19 dB', 'C/(N+I) \geq 16 dB (SINR)'}, ...
    'ylabel',     {'I/N (dB)',    'I/(N+I) (dB)',      'C/I (dB)',     'C/(N+I) (dB)'}, ...
    'lim_ok',     {-6.0,          0.97,                 19.0,          16.0}, ...
    'lim_alerta', {-3.0,          1.76,                 16.0,          10.0} ...
);

angulos_oficiales = [10 20 30 40 50 60 70 80 90];

fig = figure('Position', [50 50 1300 950], 'Color', 'w');

for k = 1:4
    crit = criterios(k);
    valores = T.(crit.columna);

    ax = subplot(2,2,k);
    hold(ax, 'on');

    % curva fina (33 puntos)
    plot(ax, theta, valores, '-', 'LineWidth', 1.6, 'Color', [0.2 0.3 0.6]);

    % resaltar los 9 puntos angulares oficiales sobre la misma curva
    [~, idx_oficiales] = ismember(angulos_oficiales, round(theta,2));
    idx_oficiales = idx_oficiales(idx_oficiales > 0);
    plot(ax, theta(idx_oficiales), valores(idx_oficiales), 'o', ...
         'MarkerSize', 7, 'MarkerFaceColor', [0.75 0.2 0.2], ...
         'MarkerEdgeColor', 'k', 'LineWidth', 1);

    yline(ax, crit.lim_ok, 'k--', 'LineWidth', 1.3);
    yline(ax, crit.lim_alerta, 'k:', 'LineWidth', 1.1);

    xlabel(ax, 'Angulo de elevacion \theta (^\circ)', 'Interpreter', 'tex');
    ylabel(ax, crit.ylabel, 'Interpreter', 'tex');
    title(ax, crit.titulo, 'Interpreter', 'tex', 'FontSize', 11);
    grid(ax, 'on');
    xlim(ax, [8 92]);
    set(ax, 'XTick', 10:10:90);

    if k == 1
        legend(ax, {'Curva fina (paso 2.5^\circ)', 'Puntos oficiales (paso 10^\circ)'}, ...
               'Location', 'northeast', 'FontSize', 8);
    end
end

sgtitle('Barrido angular fino (paso 2.5^\circ) -- 4 criterios, potencia fija', ...
        'FontWeight', 'bold', 'FontSize', 13, 'Interpreter', 'tex');

archivo_salida = fullfile(carpeta_salida, 'C_barrido_angular_fino.png');
exportgraphics(fig, archivo_salida, 'Resolution', 150);
fprintf('Grafica guardada: %s\n', archivo_salida);
