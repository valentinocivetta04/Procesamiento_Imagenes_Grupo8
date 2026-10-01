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
    idx = np.argwhere(np.diff(v))
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

    # Líneas verticales: umbral propio, más bajo porque las divisiones de Parcial 1/2/3 son más cortas (AYUDA del TP)
    img_cols = np.sum(img_th, 0)
    cols = pulsos(img_cols > 0.6 * img_cols.max())

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
            n_pal = 1 + sum(g > th_espacio for g in gaps)
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


def imagen_no_aprobados(ruta, img, img_th, filas, cols, registros):
    # Una fila por alumno con todos los campos OK y Condición Final L o R:
    # letra indicadora (roja R, azul L; colores en BGR) + crop del Nombre y Apellido.
    alumnos, salida = [], []
    for i, oks in enumerate(registros, start=1):
        c = condicion(celda(img_th, filas, cols, i, 6).astype(np.uint8)) if all(oks) else None
        if c:
            fila = cv2.copyMakeBorder(celda(img, filas, cols, i, 2), 5, 5, 40, 5, cv2.BORDER_CONSTANT, value=255)
            fila = cv2.cvtColor(fila, cv2.COLOR_GRAY2BGR)
            cv2.putText(fila, c, (10, fila.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255) if c == 'R' else (255, 0, 0), 2)
            alumnos.append(c)
            salida.append(fila)
    salida = np.vstack(salida) if salida else cv2.putText(np.full((30, 200), 255, np.uint8), 'Sin alumnos L/R', (5, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, 0, 1)

    ruta_salida = Path(ruta).with_name(f'no_aprobados_{Path(ruta).stem}.png')
    cv2.imwrite(str(ruta_salida), salida)
    print(f'Imagen de alumnos no aprobados: {ruta_salida.name} ({len(alumnos)} alumnos)')
    return alumnos


# --- Problema 2.c - CSV con los resultados de la validación -------------------
def guardar_csv(ruta, registros):
    # Una fila por registro: ID (orden en la planilla) + un OK/MAL por campo, respetando el orden de la planilla.
    ruta_csv = Path(ruta).with_name(f'validacion_{Path(ruta).stem}.csv')
    with open(ruta_csv, 'w', encoding='utf-8') as f:
        f.write('ID,Legajo,Nombre y Apellido,Parcial 1,Parcial 2,Parcial 3,Condición Final\n')   # Columnas del enunciado (c.ii)
        for i, oks in enumerate(registros, start=1):
            f.write(f'{i},' + ','.join('OK' if ok else 'MAL' for ok in oks) + '\n')
    print(f'CSV de validación: {ruta_csv.name}')


# --- Problema 2.d - Aplicación cíclica sobre las cuatro planillas --------------
if __name__ == '__main__':
    for k in range(1, 5):
        ruta = Path(__file__).parent / f'grade_sheet_{k}.png'
        print(f'\n=============== {Path(ruta).name} ===============')
        img, img_th, filas, cols, registros = validar_planilla(ruta)       # Punto a
        alumnos = imagen_no_aprobados(ruta, img, img_th, filas, cols, registros)   # Punto b
        guardar_csv(ruta, registros)                                        # Punto c

        # Informe de resultados de la planilla
        n_ok = sum(all(oks) for oks in registros)
        mal = [sum(not oks[j] for oks in registros) for j in range(len(CAMPOS))]
        print(f'Registros correctos: {n_ok} de {len(registros)}')
        print('Campos MAL: ' + ', '.join(f'{campo} {m}' for (campo, _), m in zip(CAMPOS, mal)))
        print(f'No aprobados: {alumnos.count("R")} R, {alumnos.count("L")} L')
