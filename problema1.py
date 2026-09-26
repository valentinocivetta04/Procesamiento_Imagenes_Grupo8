import cv2
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import time


# --- Problema 1.a - Ecualización local de histograma ---------------------------
def ecualizacion_local(img, M, N):
    # img : Imagen de entrada en escala de grises (2D), formato uint8.
    # M   : Alto de la ventana de procesamiento (entero positivo impar).
    # N   : Ancho de la ventana de procesamiento (entero positivo impar).
    # y   : Imagen de salida ecualizada localmente (uint8, mismo tamaño que img).
    if not (isinstance(M, (int, np.integer)) and isinstance(N, (int, np.integer)) and M > 0 and N > 0):
        raise ValueError('M y N deben ser enteros positivos.')
    if M % 2 == 0 or N % 2 == 0:
        raise ValueError('M y N deben ser impares para que la ventana tenga un píxel central.')

    # Bordes: se agregan M//2 filas arriba/abajo y N//2 columnas a izq./der.
    # replicando los valores del borde (BORDER_REPLICATE: aaaaaa|abcdefgh|hhhhhhh)
    m, n = M // 2, N // 2
    img_borde = cv2.copyMakeBorder(img, m, m, n, n, cv2.BORDER_REPLICATE)

    # Recorrido de la ventana píxel a píxel
    y = np.zeros_like(img)
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            ventana = img_borde[i:i + M, j:j + N]    # Ventana MxN centrada en (i, j)
            ventana_eq = cv2.equalizeHist(ventana)   # Transformación de ecualización local
            y[i, j] = ventana_eq[m, n]               # Sólo se conserva el píxel central
    return y


# --- Problema 1.b - Zonas de la imagen y detalles ocultos -----------------------
NOMBRES_ZONAS = ['Superior izquierda', 'Superior derecha', 'Centro', 'Inferior izquierda', 'Inferior derecha']
NOMBRES_CORTOS = ['Sup. izq.', 'Sup. der.', 'Centro', 'Inf. izq.', 'Inf. der.']

# Detalles observados en cada zona luego de la ecualización local (ver Problema1bc_explicacion.md)
DETALLES_OBSERVADOS = ['Un cuadrado pequeño',
                       'Una línea diagonal (de abajo-izq. hacia arriba-der.)',
                       'La letra "a" minúscula',
                       'Cuatro líneas horizontales paralelas',
                       'Un círculo']


def detectar_zonas(img, th=128, area_min=100):
    # img      : Imagen original en escala de grises (uint8).
    # th       : Umbral para separar los cuadrados oscuros del fondo claro.
    # area_min : Área mínima (en píxeles) para que una componente se considere una zona.
    # zonas    : Lista de (x, y, w, h) de cada cuadrado, ordenada de arriba hacia abajo y de izq. a der.
    img_th = (img < th).astype(np.uint8)
    n, labels, stats, centroids = cv2.connectedComponentsWithStats(img_th, 8, cv2.CV_32S)
    zonas = [tuple(int(v) for v in s[:4]) for s in stats[1:] if s[cv2.CC_STAT_AREA] > area_min]
    return sorted(zonas, key=lambda z: (z[1], z[0]))


def medir_detalle(zona_eq, th=128, area_min=10):
    # zona_eq  : Recorte de una zona ya ecualizada localmente (uint8).
    # th       : Umbral para quedarse con los píxeles claros (el detalle resaltado).
    # area_min : Área mínima para descartar puntos aislados de ruido.
    # Devuelve : (cantidad de objetos, ancho, alto) del rectángulo que encierra todos los objetos.
    img_th = (zona_eq > th).astype(np.uint8)
    n, labels, stats, centroids = cv2.connectedComponentsWithStats(img_th, 8, cv2.CV_32S)
    stats = stats[1:]                                  # Se descarta el fondo (etiqueta 0)
    stats = stats[stats[:, -1] > area_min, :]          # Filtrado por área (igual que la AYUDA del Problema 2)
    if len(stats) == 0:
        return 0, 0, 0
    x1, y1 = stats[:, 0].min(), stats[:, 1].min()
    x2, y2 = (stats[:, 0] + stats[:, 2]).max(), (stats[:, 1] + stats[:, 3]).max()
    return len(stats), int(x2 - x1), int(y2 - y1)


# --- Problema 1.c - Medidas para comparar tamaños de ventana --------------------
def mascaras_referencia(img, zonas, margen=2):
    # A partir de la imagen ORIGINAL arma tres máscaras booleanas:
    #   detalle     : píxeles del detalle oculto (nivel > 0 dentro de cada cuadrado).
    #   fondo_zona  : fondo oscuro de cada cuadrado, lejos del detalle.
    #   fondo_claro : fondo claro de la imagen, fuera de los cuadrados.
    # El filtro de mediana 3x3 elimina los píxeles sueltos de ruido del fondo del cuadrado,
    # y cv2.blur(...) > 0 "agranda" la máscara del detalle 2 píxeles para no mezclar bordes.
    detalle = np.zeros(img.shape, bool)
    en_zona = np.zeros(img.shape, bool)
    for (x, y, w, h) in zonas:
        detalle[y:y + h, x:x + w] = cv2.medianBlur(img[y:y + h, x:x + w], 3) > 0
        en_zona[max(y - margen, 0):y + h + margen, max(x - margen, 0):x + w + margen] = True
    detalle_ancho = cv2.blur(detalle.astype(np.uint8) * 255, (5, 5)) > 0
    fondo_zona = en_zona & ~detalle_ancho
    fondo_claro = ~en_zona
    return detalle, fondo_zona, fondo_claro


def contraste_por_zona(img_eq, zonas, detalle, fondo_zona):
    # Contraste = media del detalle - media del fondo del cuadrado, en la imagen procesada.
    # 0 => el detalle no se distingue; 255 => blanco puro sobre negro puro.
    contrastes = []
    for (x, y, w, h) in zonas:
        z = img_eq[y:y + h, x:x + w].astype(float)
        d = detalle[y:y + h, x:x + w]
        f = fondo_zona[y:y + h, x:x + w]
        contrastes.append(z[d].mean() - z[f].mean())
    return contrastes


def ruido_fondo(img_eq, fondo_claro, th=128):
    # Porcentaje de píxeles del fondo claro que quedaron oscuros (< th) luego del procesamiento.
    return 100 * np.mean(img_eq[fondo_claro] < th)


if __name__ == '__main__':
    ruta = Path(__file__).parent / 'Imagen_con_detalles_escondidos.tif'
    img = cv2.imread(str(ruta), cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError(f'No se pudo cargar la imagen desde {ruta}')

    # =========================================================================
    # Punto B - Análisis de la imagen con la ecualización local
    # =========================================================================
    M_b, N_b = 21, 21                           # Ventana elegida a partir del análisis del punto C
    zonas = detectar_zonas(img)
    img_eq_global = cv2.equalizeHist(img)
    img_eq_local = ecualizacion_local(img, M_b, N_b)

    # Figura 1: original vs. ecualización global vs. ecualización local
    plt.figure('Punto B - Global vs. local')
    ax1 = plt.subplot(131)
    plt.imshow(img, cmap='gray', vmin=0, vmax=255)
    plt.title('Imagen Original')
    plt.xticks([]), plt.yticks([])
    plt.subplot(132, sharex=ax1, sharey=ax1)
    plt.imshow(img_eq_global, cmap='gray', vmin=0, vmax=255)
    plt.title('Ecualización global')
    plt.xticks([]), plt.yticks([])
    plt.subplot(133, sharex=ax1, sharey=ax1)
    plt.imshow(img_eq_local, cmap='gray', vmin=0, vmax=255)
    plt.title(f'Ecualización local ({M_b}x{N_b})')
    plt.xticks([]), plt.yticks([])

    # Figura 2: zoom de cada zona, original (arriba) y ecualizada localmente (abajo)
    plt.figure('Punto B - Detalles por zona')
    for k, (x, y, w, h) in enumerate(zonas):
        plt.subplot(2, len(zonas), k + 1)
        plt.imshow(img[y:y + h, x:x + w], cmap='gray', vmin=0, vmax=255)
        plt.title(f'{NOMBRES_ZONAS[k]}\n(original)', fontsize=9)
        plt.xticks([]), plt.yticks([])
        plt.subplot(2, len(zonas), len(zonas) + k + 1)
        plt.imshow(img_eq_local[y:y + h, x:x + w], cmap='gray', vmin=0, vmax=255)
        plt.title(f'{DETALLES_OBSERVADOS[k]}', fontsize=9)
        plt.xticks([]), plt.yticks([])

    # Informe por consola
    print(f'\n--- Punto B: detalles ocultos (ventana {M_b}x{N_b}) ---')
    for k, (x, y, w, h) in enumerate(zonas):
        zona_orig = img[y:y + h, x:x + w]
        cant, ancho, alto = medir_detalle(img_eq_local[y:y + h, x:x + w])
        print(f'> Zona {NOMBRES_ZONAS[k]:<19} (x={x:3d}, y={y:3d}, {w}x{h} px) | '
              f'niveles originales {zona_orig.min()}..{zona_orig.max()} | '
              f'{cant} objeto(s), {ancho}x{alto} px | {DETALLES_OBSERVADOS[k]}')

    # =========================================================================
    # Punto C - Influencia del tamaño de la ventana
    # =========================================================================
    detalle, fondo_zona, fondo_claro = mascaras_referencia(img, zonas)

    ventanas = [(3, 3), (5, 5), (7, 7), (9, 9), (15, 15), (21, 21), (31, 31),
                (45, 45), (61, 61), (81, 81), (101, 101),     # cuadradas
                (3, 31), (31, 3), (1, 61), (61, 1)]           # rectangulares (M alto x N ancho)
    resultados = {}
    print('\n--- Punto C: influencia del tamaño de ventana ---')
    print(f'{"Ventana":>9} | {"Contraste medio":>15} | ' + ' | '.join(f'{z:>9}' for z in NOMBRES_CORTOS)
          + f' | {"Ruido fondo":>11} | {"Tiempo":>6}')
    for (M, N) in ventanas:
        t0 = time.time()
        y_eq = ecualizacion_local(img, M, N)
        dt = time.time() - t0
        c = contraste_por_zona(y_eq, zonas, detalle, fondo_zona)
        r = ruido_fondo(y_eq, fondo_claro)
        resultados[(M, N)] = (y_eq, c, r, dt)
        print(f'{M:>4}x{N:<4} | {np.mean(c):15.1f} | ' + ' | '.join(f'{v:9.1f}' for v in c)
              + f' | {r:10.1f}% | {dt:5.2f}s')
    c = contraste_por_zona(img_eq_global, zonas, detalle, fondo_zona)
    print(f'{"Global":>9} | {np.mean(c):15.1f} | ' + ' | '.join(f'{v:9.1f}' for v in c)
          + f' | {ruido_fondo(img_eq_global, fondo_claro):10.1f}% |')

    # Figura 3: imagen completa con distintas ventanas cuadradas
    cuadradas = [(3, 3), (7, 7), (15, 15), (21, 21), (31, 31), (61, 61), (101, 101)]
    plt.figure('Punto C - Ventanas cuadradas')
    ax1 = plt.subplot(331)
    plt.imshow(img, cmap='gray', vmin=0, vmax=255)
    plt.title('Imagen Original')
    plt.xticks([]), plt.yticks([])
    plt.subplot(332, sharex=ax1, sharey=ax1)
    plt.imshow(img_eq_global, cmap='gray', vmin=0, vmax=255)
    plt.title('Ecualización global')
    plt.xticks([]), plt.yticks([])
    for k, (M, N) in enumerate(cuadradas):
        plt.subplot(3, 3, k + 3, sharex=ax1, sharey=ax1)
        plt.imshow(resultados[(M, N)][0], cmap='gray', vmin=0, vmax=255)
        plt.title(f'Ecualización local ({M}x{N})')
        plt.xticks([]), plt.yticks([])

    # Figura 4: zoom de cada zona (columnas) para cada ventana (filas)
    plt.figure('Punto C - Zonas vs. tamaño de ventana')
    for f, (M, N) in enumerate(cuadradas):
        for k, (x, y, w, h) in enumerate(zonas):
            plt.subplot(len(cuadradas), len(zonas), f * len(zonas) + k + 1)
            plt.imshow(resultados[(M, N)][0][y:y + h, x:x + w], cmap='gray', vmin=0, vmax=255)
            plt.xticks([]), plt.yticks([])
            if k == 0:
                plt.ylabel(f'{M}x{N}', fontsize=9)
            if f == 0:
                plt.title(NOMBRES_ZONAS[k], fontsize=9)

    # Figura 5: ventanas rectangulares (la orientación de la ventana importa)
    rectangulares = [(3, 31), (31, 3), (1, 61), (61, 1)]
    plt.figure('Punto C - Ventanas rectangulares')
    ax1 = plt.subplot(231)
    plt.imshow(img, cmap='gray', vmin=0, vmax=255)
    plt.title('Imagen Original')
    plt.xticks([]), plt.yticks([])
    plt.subplot(232, sharex=ax1, sharey=ax1)
    plt.imshow(resultados[(21, 21)][0], cmap='gray', vmin=0, vmax=255)
    plt.title('Referencia (21x21)')
    plt.xticks([]), plt.yticks([])
    for k, (M, N) in enumerate(rectangulares):
        plt.subplot(2, 3, k + 3, sharex=ax1, sharey=ax1)
        plt.imshow(resultados[(M, N)][0], cmap='gray', vmin=0, vmax=255)
        plt.title(f'Ecualización local ({M}x{N})')
        plt.xticks([]), plt.yticks([])

    # Figura 6: medidas vs. tamaño de ventana (sólo ventanas cuadradas)
    lados = [M for (M, N) in ventanas if M == N]
    plt.figure('Punto C - Medidas vs. tamaño de ventana')
    plt.subplot(131)
    for k in range(len(zonas)):
        plt.plot(lados, [resultados[(L, L)][1][k] for L in lados], 'o-', label=NOMBRES_ZONAS[k])
    plt.axvline(zonas[0][2], color='gray', linestyle='--', label='Lado de los cuadrados')
    plt.xlabel('Lado de la ventana (px)'), plt.ylabel('Contraste detalle - fondo')
    plt.title('Contraste por zona'), plt.legend(fontsize=8), plt.grid(True)
    plt.subplot(132)
    plt.plot(lados, [resultados[(L, L)][2] for L in lados], 'o-')
    plt.xlabel('Lado de la ventana (px)'), plt.ylabel('% de píxeles oscurecidos')
    plt.title('Ruido en el fondo claro'), plt.grid(True)
    plt.subplot(133)
    plt.plot(lados, [resultados[(L, L)][3] for L in lados], 'o-')
    plt.xlabel('Lado de la ventana (px)'), plt.ylabel('Segundos')
    plt.title('Tiempo de ejecución'), plt.grid(True)

    plt.show()
