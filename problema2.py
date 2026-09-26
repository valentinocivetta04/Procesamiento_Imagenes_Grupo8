import sys
import cv2
import numpy as np
from pathlib import Path


# --- Problema 2.a - Validación de los campos de una planilla -------------------
# Regla de cada campo en función de (cantidad de caracteres, cantidad de palabras)
CAMPOS = [('Legajo',            lambda c, p: c == 8 and p == 1),
          ('Nombre y apellido', lambda c, p: p >= 2 and c <= 12),
          ('Parcial 1',         lambda c, p: 1 <= c <= 2 and p == 1),
          ('Parcial 2',         lambda c, p: 1 <= c <= 2 and p == 1),
          ('Parcial 3',         lambda c, p: 1 <= c <= 2 and p == 1),
          ('Condición Final',   lambda c, p: c == 1)]


def pulsos(v):
    # v : Vector booleano. Devuelve una fila [inicio, fin] por cada tramo de valores True.
    # (Técnica "Encontrar inicio/fin de pulsos" de PDI_U1_p1_Letras.py)
    idx = np.argwhere(np.diff(v)).ravel()
    idx[0::2] += 1
    return idx.reshape(-1, 2)


def validar_planilla(ruta, th=150, th_area=1, th_espacio=6):
    # ruta       : Imagen de la planilla (grade_sheet_<id>.png).
    # th         : Umbral de intensidad: texto y líneas de la tabla quedan en True.
    # th_area    : Área mínima de una componente para considerarla un caracter.
    # th_espacio : Separación horizontal mínima (px) entre caracteres para considerar que hay un espacio.
    img = cv2.imread(str(ruta), cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError(f'No se pudo cargar la imagen desde {ruta}')
    img_th = img < th

    # Líneas horizontales: filas con muchos más píxeles oscuros que el resto (AYUDA del TP)
    img_rows = np.sum(img_th, 1)
    filas = pulsos(img_rows > 0.8 * img_rows.max())

    # Líneas verticales: sólo en la zona de registros (entre la línea bajo el encabezado y la última),
    # así las divisiones de Parcial 1/2/3 tienen el mismo largo que las demás.
    img_cols = np.sum(img_th[filas[1, 1]:filas[-1, 0]], 0)
    cols = pulsos(img_cols > 0.8 * img_cols.max())

    for i in range(1, len(filas) - 1):                  # Cada registro está entre dos líneas horizontales
        print(f'> Registro {i}:')
        for j, (campo, regla) in enumerate(CAMPOS, start=1):   # j = 0 es la columna "Nro.", se saltea
            celda = img_th[filas[i, 1] + 1:filas[i + 1, 0], cols[j, 1] + 1:cols[j + 1, 0]].astype(np.uint8)
            _, _, stats, _ = cv2.connectedComponentsWithStats(celda, 8, cv2.CV_32S)
            stats = stats[1:]                               # Se descarta el fondo (etiqueta 0)
            stats = stats[stats[:, -1] > th_area, :]        # Filtrado por área (AYUDA del TP)
            stats = sorted(stats, key=lambda s: s[0])       # Caracteres ordenados de izquierda a derecha
            gaps = [b[0] - (a[0] + a[2]) for a, b in zip(stats, stats[1:])]  # Columnas vacías entre caracteres
            n_car = len(stats)
            n_pal = 0 if n_car == 0 else 1 + sum(g > th_espacio for g in gaps)
            print(f'> {campo}: {"OK" if regla(n_car, n_pal) else "MAL"}')
        print('>')


if __name__ == '__main__':
    validar_planilla(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).parent / 'grade_sheet_1.png')
