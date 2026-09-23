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


if __name__ == '__main__':
    ruta = Path(__file__).parent / 'Imagen_con_detalles_escondidos.tif'
    img = cv2.imread(str(ruta), cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError(f'No se pudo cargar la imagen desde {ruta}')

    # Tamaños de ventana a probar (M x N)
    ventanas = [(3, 3), (7, 7), (15, 15), (27, 27), (31, 31), (23, 23), (61, 61)]

    ax1 = plt.subplot(231)
    plt.imshow(img, cmap='gray', vmin=0, vmax=255)
    plt.title('Imagen Original')
    plt.xticks([]), plt.yticks([])

    for k, (M, N) in enumerate(ventanas):
        img_eq_local = ecualizacion_local(img, M, N)
        plt.subplot(3, 3, k + 2, sharex=ax1, sharey=ax1)
        plt.imshow(img_eq_local, cmap='gray', vmin=0, vmax=255)
        plt.title(f'Ecualización local ({M}x{N})')
        plt.xticks([]), plt.yticks([])

    plt.show()
