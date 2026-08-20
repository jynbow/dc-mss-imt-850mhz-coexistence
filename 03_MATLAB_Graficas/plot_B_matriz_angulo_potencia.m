%% plot_B_matriz_angulo_potencia.m
% ============================================================
% Grafica los resultados del Script B (matriz 9 angulos x 15 potencias,
% proyecto de investigacion). Para CADA uno de los 4 criterios genera:
%   (a) Tabla anotada tipo semaforo (valor exacto + color por zona)
%   (b) Mapa circular (anillos=angulo, sectores=potencia)
%   (c) Curvas por nivel de potencia (eje X = angulo)
%
% ENTRADA:  ../02_Resultados_CSV/B_barrido_angulo_potencia_SHARC.csv
% SALIDA:   ../04_Graficas_Generadas/B_criterio_<NOMBRE>.png  (4 archivos)
%
% Como usar: abrir en MATLAB y presionar "Run" (F5). No hace falta
% cambiar nada si respetaste la estructura de carpetas del ZIP.
% ============================================================

clear; clc; close all;

carpeta_datos  = fullfile('..', '02_Resultados_CSV');
carpeta_salida = fullfile('..', '04_Graficas_Generadas');
if ~exist(carpeta_salida, 'dir')
    mkdir(carpeta_salida);
end

archivo = fullfile(carpeta_datos, 'B_barrido_angulo_potencia_SHARC.csv');
if ~exist(archivo, 'file')
    error(['No se encontro el archivo: ' archivo newline ...
           'Corre primero B_barrido_angulo_potencia_p619.py en Python ' ...
           'y copia el CSV generado a la carpeta 02_Resultados_CSV.']);
end

T = readtable(archivo);

thetas = unique(T.theta_deg);          % 9 angulos
ptxs   = flipud(unique(T.ptx_sat_dbm)); % 15 potencias, orden 43->1
n_r = numel(thetas);
n_c = numel(ptxs);

% ---- definicion de los 4 criterios (columna, umbrales, direccion) ----
criterios = struct( ...
    'nombre',   {'IN',                         'INI',                          'CI',                     'CNI'}, ...
    'columna',  {'IN_db',                      'INI_db',                       'CI_db',                  'CNI_db'}, ...
    'titulo',   {'Criterio 1 -- I/N \leq -6 dB', 'Criterio 2 -- I/(N+I) \leq 0.97 dB', 'Criterio 3 -- C/I \geq 19 dB', 'Criterio 4 -- C/(N+I) \geq 16 dB (SINR)'}, ...
    'ylabel',   {'I/N (dB)',                   'I/(N+I) (dB)',                 'C/I (dB)',                'C/(N+I) (dB)'}, ...
    'mejor',    {'menor',                      'menor',                        'mayor',                   'mayor'}, ...
    'lim_ok',   {-6.0,                         0.97,                           19.0,                      16.0}, ...
    'lim_alerta', {-3.0,                       1.76,                           16.0,                      10.0} ...
);

VERDE_CLARO = [0.85 0.95 0.85]; VERDE_OSCURO = [0.11 0.37 0.13];
AMAR_CLARO  = [1.00 0.97 0.84]; AMAR_OSCURO  = [0.90 0.31 0.00];
ROJO_CLARO  = [1.00 0.85 0.85]; ROJO_OSCURO  = [0.55 0.00 0.00];

for k = 1:numel(criterios)
    crit = criterios(k);
    valores = T.(crit.columna);

    % ---- armar la grilla 9x15 (filas=angulo, columnas=potencia) ----
    G = nan(n_r, n_c);
    for i = 1:n_r
        for j = 1:n_c
            m = (T.theta_deg == thetas(i)) & (T.ptx_sat_dbm == ptxs(j));
            G(i,j) = valores(find(m,1));
        end
    end

    % ---- clasificar por zona y calcular color con matiz de margen ----
    [colores, zonas] = colorear_por_zona(G, crit.lim_ok, crit.lim_alerta, crit.mejor, ...
                            VERDE_CLARO, VERDE_OSCURO, AMAR_CLARO, AMAR_OSCURO, ROJO_CLARO, ROJO_OSCURO);

    fig = figure('Position', [50 50 1700 650], 'Color', 'w');

    % ================= (a) TABLA ANOTADA =================
    ax1 = subplot(1,3,1);
    hold(ax1, 'on');
    for i = 1:n_r
        for j = 1:n_c
            x0 = j-1; y0 = n_r-i; % fila 1 (10 grados) arriba
            patch(ax1, [x0 x0+1 x0+1 x0], [y0 y0 y0+1 y0+1], squeeze(colores(i,j,:))', ...
                  'EdgeColor', 'w', 'LineWidth', 0.5);
            brillo = 0.299*colores(i,j,1) + 0.587*colores(i,j,2) + 0.114*colores(i,j,3);
            if brillo < 0.55
                txt_color = 'w';
            else
                txt_color = 'k';
            end
            text(ax1, x0+0.5, y0+0.5, sprintf('%.1f', G(i,j)), ...
                 'HorizontalAlignment', 'center', 'VerticalAlignment', 'middle', ...
                 'FontSize', 6.5, 'Color', txt_color);
        end
    end
    xlim(ax1, [0 n_c]); ylim(ax1, [0 n_r]);
    set(ax1, 'XTick', 0.5:1:n_c-0.5, 'XTickLabel', string(ptxs), 'XTickLabelRotation', 90, 'FontSize', 7);
    set(ax1, 'YTick', 0.5:1:n_r-0.5, 'YTickLabel', string(flipud(thetas)) + "^\circ", 'FontSize', 8);
    xlabel(ax1, 'Potencia Tx satelite (dBm)');
    ylabel(ax1, 'Angulo de elevacion \theta (^\circ)', 'Interpreter', 'tex');
    title(ax1, '(a) Tabla -- valor exacto + matiz de margen', 'FontSize', 10);
    box(ax1, 'on');

    % ================= (b) MAPA CIRCULAR (anillos=angulo, sectores=potencia) =====
    ax2 = subplot(1,3,2);
    hold(ax2, 'on'); axis(ax2, 'equal'); axis(ax2, 'off');
    r_edges = linspace(0, 50, n_r+1);
    th_edges = linspace(0, 2*pi, n_c+1) + pi/2;   % 0 grados arriba (Norte)
    for i = 1:n_r
        for j = 1:n_c
            th0 = th_edges(j); th1 = th_edges(j+1);
            r0 = r_edges(i); r1 = r_edges(i+1);
            th_arc = linspace(th0, th1, 6);
            xin  = r0*cos(th_arc);  yin  = r0*sin(th_arc);
            xout = r1*cos(fliplr(th_arc)); yout = r1*sin(fliplr(th_arc));
            patch(ax2, [xin xout], [yin yout], squeeze(colores(i,j,:))', ...
                  'EdgeColor', [1 1 1], 'LineWidth', 0.3);
        end
    end
    % etiquetas de angulo (radiales) y potencia (alrededor del borde)
    for i = 1:n_r
        text(ax2, 0, r_edges(i+1), sprintf('%g^\\circ', thetas(i)), ...
             'FontSize', 6.5, 'HorizontalAlignment', 'center', 'VerticalAlignment', 'bottom');
    end
    for j = 1:n_c
        th_mid = (th_edges(j)+th_edges(j+1))/2;
        text(ax2, 53*cos(th_mid), 53*sin(th_mid), sprintf('%gdBm', ptxs(j)), ...
             'FontSize', 6, 'HorizontalAlignment', 'center');
    end
    xlim(ax2, [-62 62]); ylim(ax2, [-62 62]);
    title(ax2, {'(b) Mapa circular -- mismo esquema de color que (a)', ...
                'anillos=angulo, sectores=potencia'}, 'FontSize', 10);

    % ================= (c) CURVAS por potencia =================
    ax3 = subplot(1,3,3);
    hold(ax3, 'on');
    cmap = parula(n_c);
    for j = 1:n_c
        plot(ax3, thetas, G(:,j), '-o', 'LineWidth', 1.4, 'MarkerSize', 3, 'Color', cmap(j,:));
        if mod(j,2) == 1
            text(ax3, thetas(end)+1, G(end,j), sprintf('%gdBm', ptxs(j)), ...
                 'FontSize', 6.5, 'Color', cmap(j,:), 'FontWeight', 'bold');
        end
    end
    yline(ax3, crit.lim_ok, 'k--', 'LineWidth', 1.4);
    yline(ax3, crit.lim_alerta, 'k:', 'LineWidth', 1.2);
    xlabel(ax3, 'Angulo de elevacion \theta (^\circ)');
    ylabel(ax3, crit.ylabel, 'Interpreter', 'tex');
    title(ax3, '(c) Curvas por nivel de potencia', 'FontSize', 10);
    grid(ax3, 'on');
    xlim(ax3, [thetas(1)-3, thetas(end)+9]);

    sgtitle(crit.titulo, 'FontWeight', 'bold', 'FontSize', 13, 'Interpreter', 'tex');

    archivo_salida = fullfile(carpeta_salida, sprintf('B_criterio_%s.png', crit.nombre));
    exportgraphics(fig, archivo_salida, 'Resolution', 150);
    fprintf('Grafica guardada: %s\n', archivo_salida);
end


%% ---- funcion local: clasificar por zona y asignar color con matiz ----
function [colores, zonas] = colorear_por_zona(G, lim_ok, lim_alerta, mejor, ...
                                v_clr, v_osc, a_clr, a_osc, r_clr, r_osc)
    [n_r, n_c] = size(G);
    zonas = zeros(n_r, n_c);
    colores = zeros(n_r, n_c, 3);

    if strcmp(mejor, 'menor')
        margen_bueno = lim_ok - G;
        margen_malo  = G - lim_alerta;
        ancho = lim_alerta - lim_ok;
        t_alerta = (G - lim_ok) / ancho;
        zonas(G <= lim_ok) = 0;
        zonas(G > lim_ok & G <= lim_alerta) = 1;
        zonas(G > lim_alerta) = 2;
    else
        margen_bueno = G - lim_ok;
        margen_malo  = lim_alerta - G;
        ancho = lim_ok - lim_alerta;
        t_alerta = (lim_ok - G) / ancho;
        zonas(G >= lim_ok) = 0;
        zonas(G < lim_ok & G >= lim_alerta) = 1;
        zonas(G < lim_alerta) = 2;
    end

    mask0 = zonas == 0; mask2 = zonas == 2;
    max_bueno = max(margen_bueno(mask0)); if isempty(max_bueno) || max_bueno <= 0, max_bueno = 1; end
    max_malo  = max(margen_malo(mask2));  if isempty(max_malo)  || max_malo  <= 0, max_malo  = 1; end

    for i = 1:n_r
        for j = 1:n_c
            z = zonas(i,j);
            if z == 0
                t = max(0, min(1, margen_bueno(i,j) / max_bueno));
                colores(i,j,:) = v_clr + (v_osc - v_clr) * t;
            elseif z == 1
                t = max(0, min(1, t_alerta(i,j)));
                colores(i,j,:) = a_clr + (a_osc - a_clr) * t;
            else
                t = max(0, min(1, margen_malo(i,j) / max_malo));
                colores(i,j,:) = r_clr + (r_osc - r_clr) * t;
            end
        end
    end
end
