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


def celda(m, filas, cols, i, j):
    # Recorte de la celda (registro i, columna j) sin las líneas de la tabla.
    return m[filas[i, 1] + 1:filas[i + 1, 0], cols[j, 1] + 1:cols[j + 1, 0]]


def validar_planilla(ruta, th=150, th_area=1, th_espacio=6):
    # ruta       : Imagen de la planilla (grade_sheet_<id>.png).
    # th         : Umbral de intensidad: texto y líneas de la tabla quedan en True.
    # th_area    : Área mínima de una componente para considerarla un caracter.
    # th_espacio : Separación horizontal mínima (px) entre caracteres para considerar que hay un espacio.
    # Devuelve   : img, img_th, filas, cols y, por registro, la lista de campos OK (True) / MAL (False).
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

    registros = []
    for i in range(1, len(filas) - 1):                  # Cada registro está entre dos líneas horizontales
        print(f'> Registro {i}:')
        oks = []
        for j, (campo, regla) in enumerate(CAMPOS, start=1):   # j = 0 es la columna "Nro.", se saltea
            _, _, stats, _ = cv2.connectedComponentsWithStats(celda(img_th, filas, cols, i, j).astype(np.uint8), 8, cv2.CV_32S)
            stats = stats[1:]                               # Se descarta el fondo (etiqueta 0)
            stats = stats[stats[:, -1] > th_area, :]        # Filtrado por área (AYUDA del TP)
            stats = sorted(stats, key=lambda s: s[0])       # Caracteres ordenados de izquierda a derecha
            gaps = [b[0] - (a[0] + a[2]) for a, b in zip(stats, stats[1:])]  # Columnas vacías entre caracteres
            n_car = len(stats)
            n_pal = 0 if n_car == 0 else 1 + sum(g > th_espacio for g in gaps)
            oks.append(regla(n_car, n_pal))
            print(f'> {campo}: {"OK" if oks[-1] else "MAL"}')
        print('>')
        registros.append(oks)
    return img, img_th, filas, cols, registros


# --- Problema 2.b - Imagen con los alumnos que no aprobaron --------------------
def condicion(letra):
    # letra : Celda binaria (uint8) de Condición Final con un único caracter.
    # Devuelve 'L', 'R' o None (A u otro caracter).
    #   - L y R tienen la columna izquierda llena (trazo vertical); la A no (empieza en diagonal).
    #   - La R tiene un agujero (un contorno con madre en la jerarquía); la L no.
    _, _, stats, _ = cv2.connectedComponentsWithStats(letra, 8, cv2.CV_32S)
    x, y, w, h = stats[1, :4]
    if np.sum(letra[y:y + h, x:x + w], 0)[0] < h:       # Suma por columnas (AYUDA del TP)
        return None
    contours, hierarchy = cv2.findContours(letra, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    agujeros = sum(hh[3] != -1 for hh in hierarchy[0])  # hierarchy: [Next, Previous, First_Child, Parent]
    return 'R' if agujeros else 'L'


def imagen_no_aprobados(ruta, sep=10, ancho_etiqueta=40):
    # Arma una única imagen con el recorte del Nombre y Apellido de cada alumno con todos los campos OK
    # y Condición Final L o R. Indicador: letra y recuadro rojos para R, azules para L (colores en BGR).
    img, img_th, filas, cols, registros = validar_planilla(ruta)
    alumnos = [(condicion(celda(img_th, filas, cols, i, 6).astype(np.uint8)), celda(img, filas, cols, i, 2))
               for i, oks in enumerate(registros, start=1) if all(oks)]
    alumnos = [(c, nombre) for c, nombre in alumnos if c]

    h, w = celda(img, filas, cols, 1, 2).shape
    salida = np.full((max(len(alumnos), 1) * (h + sep) + sep, ancho_etiqueta + w + sep, 3), 255, np.uint8)
    if not alumnos:
        cv2.putText(salida, 'Sin alumnos L/R', (sep, h), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
    for k, (c, nombre) in enumerate(alumnos):
        y0, x0 = sep + k * (h + sep), ancho_etiqueta
        color = (0, 0, 255) if c == 'R' else (255, 0, 0)
        salida[y0:y0 + h, x0:x0 + w] = cv2.cvtColor(nombre, cv2.COLOR_GRAY2BGR)     # Pego el recorte
        cv2.rectangle(salida, (x0 - 1, y0 - 1), (x0 + w, y0 + h), color, 2)
        cv2.putText(salida, c, (10, y0 + h // 2 + 8), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

    ruta_salida = Path(ruta).with_name(f'no_aprobados_{Path(ruta).stem}.png')
    cv2.imwrite(str(ruta_salida), salida)
    print(f'Imagen de alumnos no aprobados: {ruta_salida.name} ({len(alumnos)} alumnos)')
    return alumnos


if __name__ == '__main__':
    imagen_no_aprobados(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).parent / 'grade_sheet_1.png')
