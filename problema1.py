import cv2
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path


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
# Esquina superior izquierda (x, y) de cada cuadrado oscuro de 62x62 px, medida a mano sobre la imagen,
# y detalle observado en cada uno luego de la ecualización local (ver Problema1bc_explicacion.md)
ZONAS = [('Superior izquierda', 6, 6, 'Un cuadrado pequeño'),
         ('Superior derecha', 187, 6, 'Una línea diagonal (de abajo-izq. hacia arriba-der.)'),
         ('Centro', 97, 97, 'La letra "a" minúscula'),
         ('Inferior izquierda', 6, 188, 'Cuatro líneas horizontales paralelas'),
         ('Inferior derecha', 187, 188, 'Un círculo')]
L = 62


if __name__ == '__main__':
    ruta = Path(__file__).parent / 'Imagen_con_detalles_escondidos.tif'
    img = cv2.imread(str(ruta), cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError(f'No se pudo cargar la imagen desde {ruta}')

    # =========================================================================
    # Punto B - Análisis de la imagen con la ecualización local
    # =========================================================================
    M_b, N_b = 21, 21                           # Ventana elegida a partir del análisis del punto C
    img_heq = cv2.equalizeHist(img)
    img_eq_local = ecualizacion_local(img, M_b, N_b)

    # Figura 1: original vs. ecualización global vs. ecualización local
    plt.figure('Punto B - Global vs. local')
    ax1 = plt.subplot(131)
    plt.imshow(img, cmap='gray', vmin=0, vmax=255)
    plt.title('Imagen Original')
    plt.xticks([]), plt.yticks([])
    plt.subplot(132, sharex=ax1, sharey=ax1)
    plt.imshow(img_heq, cmap='gray', vmin=0, vmax=255)
    plt.title('Ecualización global')
    plt.xticks([]), plt.yticks([])
    plt.subplot(133, sharex=ax1, sharey=ax1)
    plt.imshow(img_eq_local, cmap='gray', vmin=0, vmax=255)
    plt.title(f'Ecualización local ({M_b}x{N_b})')
    plt.xticks([]), plt.yticks([])

    # Figura 2: zoom de cada zona, original (arriba) y ecualizada localmente (abajo) + informe por consola
    print(f'\n--- Punto B: detalles ocultos (ventana {M_b}x{N_b}) ---')
    plt.figure('Punto B - Detalles por zona')
    for k, (nombre, x, y, detalle) in enumerate(ZONAS):
        plt.subplot(2, 5, k + 1)
        plt.imshow(img[y:y + L, x:x + L], cmap='gray', vmin=0, vmax=255)
        plt.title(f'{nombre}\n(original)', fontsize=9)
        plt.xticks([]), plt.yticks([])
        plt.subplot(2, 5, k + 6)
        plt.imshow(img_eq_local[y:y + L, x:x + L], cmap='gray', vmin=0, vmax=255)
        plt.title(detalle, fontsize=9)
        plt.xticks([]), plt.yticks([])
        print(f'> {nombre}: {detalle}')

    # =========================================================================
    # Punto C - Influencia del tamaño de la ventana (comparación visual)
    # =========================================================================
    # Figura 3: imagen completa con distintas ventanas cuadradas
    cuadradas = [(3, 3), (7, 7), (15, 15), (21, 21), (31, 31), (61, 61), (101, 101)]
    plt.figure('Punto C - Ventanas cuadradas')
    ax1 = plt.subplot(331)
    plt.imshow(img, cmap='gray', vmin=0, vmax=255)
    plt.title('Imagen Original')
    plt.xticks([]), plt.yticks([])
    plt.subplot(332, sharex=ax1, sharey=ax1)
    plt.imshow(img_heq, cmap='gray', vmin=0, vmax=255)
    plt.title('Ecualización global')
    plt.xticks([]), plt.yticks([])
    for k, (M, N) in enumerate(cuadradas):
        plt.subplot(3, 3, k + 3, sharex=ax1, sharey=ax1)
        plt.imshow(ecualizacion_local(img, M, N), cmap='gray', vmin=0, vmax=255)
        plt.title(f'Ecualización local ({M}x{N})')
        plt.xticks([]), plt.yticks([])

    # Figura 4: ventanas rectangulares (la orientación de la ventana importa)
    rectangulares = [(3, 31), (31, 3), (1, 61), (61, 1)]
    plt.figure('Punto C - Ventanas rectangulares')
    ax1 = plt.subplot(231)
    plt.imshow(img, cmap='gray', vmin=0, vmax=255)
    plt.title('Imagen Original')
    plt.xticks([]), plt.yticks([])
    plt.subplot(232, sharex=ax1, sharey=ax1)
    plt.imshow(img_eq_local, cmap='gray', vmin=0, vmax=255)
    plt.title(f'Referencia ({M_b}x{N_b})')
    plt.xticks([]), plt.yticks([])
    for k, (M, N) in enumerate(rectangulares):
        plt.subplot(2, 3, k + 3, sharex=ax1, sharey=ax1)
        plt.imshow(ecualizacion_local(img, M, N), cmap='gray', vmin=0, vmax=255)
        plt.title(f'Ecualización local ({M}x{N})')
        plt.xticks([]), plt.yticks([])

    plt.show()
