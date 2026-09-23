# TP1 PDI – Problema 1a: Ecualización local de histograma

Procesamiento de Imágenes I (IA 4.4) · TUIA – FCEIA – UNR · 2026, 2° semestre

---

## 1. Qué pide el enunciado (Problema 1, punto a)

> Desarrolle una función para implementar la ecualización local de histograma, que reciba como parámetros de entrada la imagen a procesar y el tamaño de la ventana de procesamiento (M×N con M, N ∈ Z⁺).

**Ayuda del enunciado:** usar `cv2.copyMakeBorder(img, top, bottom, left, right, borderType)` para agregar píxeles alrededor de la imagen. Con `borderType = cv2.BORDER_REPLICATE` se replican los valores del borde.

**Imagen del TP:** `Imagen_con_detalles_escondidos.tif` (256×256, uint8).

---

## 2. Marco teórico

### 2.1 Histograma

El histograma de una imagen en escala de grises cuenta cuántos píxeles hay de cada nivel de intensidad r_k (k = 0 … L−1, con L = 256 para uint8):

- Histograma: `h(r_k) = n_k`
- Histograma normalizado (probabilidad de cada nivel): `p(r_k) = n_k / (total de píxeles)`

La cátedra usa tres formas de calcularlo:

| Función | Uso |
|---|---|
| `cv2.calcHist()` | La más rápida, soporta varios canales y máscaras |
| `np.histogram()` | Velocidad media, cualquier tipo de dato, sin máscaras ni varios canales |
| `plt.hist()` | La más lenta, pensada solo para visualizar |

*(Fuente: comentario en `PDI_U2_p2_stain.py` y comparación `hist` vs `hist2` en `PI_U2_Transformacion_y_Filtrado_p1.py`)*

### 2.2 Ecualización global de histograma

El objetivo es redistribuir las intensidades para que el histograma quede lo más uniforme posible y así aumentar el contraste. La transformación es la **función de distribución acumulada (CDF)** escalada al rango de salida:

```
s_k = T(r_k) = (L − 1) · Σ_{j=0..k} p(r_j)
```

En la cátedra aparece como `histn = hist / img.size` y `cdf = histn.cumsum()`, y la función que la aplica es `cv2.equalizeHist(img)`.

**Limitación:** el histograma se calcula con **todos** los píxeles de la imagen. Si un detalle tiene una intensidad casi igual a la de su fondo local y ocupa pocos píxeles, casi no pesa en el histograma global y la ecualización no lo resalta. Se pierde la información local.

### 2.3 Ecualización local de histograma

Es la extensión local de la técnica anterior:

1. Se define una ventana M×N.
2. Se centra la ventana en un píxel.
3. Se calcula el histograma **solo de los píxeles de la ventana** y su transformación de ecualización.
4. Esa transformación se aplica **solo al píxel central**.
5. La ventana se desplaza un píxel y se repite hasta recorrer toda la imagen.

Como la CDF sale de los vecinos, diferencias muy chicas de intensidad dentro de una zona casi uniforme se estiran a todo el rango [0, 255]. Por eso aparecen los detalles escondidos.

### 2.4 Por qué M y N tienen que ser impares

La ventana se centra en cada píxel. Para que haya **un único píxel central**, la ventana necesita la misma cantidad de píxeles a cada lado: M = 2m + 1 y N = 2n + 1. Con un tamaño par, el centro queda entre dos píxeles.

### 2.5 Tratamiento de bordes

Cuando el píxel central está cerca del borde, parte de la ventana cae fuera de la imagen. Por eso se agregan m = M//2 filas arriba y abajo y n = N//2 columnas a izquierda y derecha. Los tipos de borde de OpenCV son:

```
BORDER_REPLICATE:     aaaaaa|abcdefgh|hhhhhhh
BORDER_REFLECT:       fedcba|abcdefgh|hgfedcb
BORDER_REFLECT_101:   gfedcb|abcdefgh|gfedcba
BORDER_WRAP:          cdefgh|abcdefgh|abcdefg
BORDER_CONSTANT:      iiiiii|abcdefgh|iiiiiii  (con algún valor 'i')
```

Se usa `BORDER_REPLICATE` porque copia el valor del borde y no agrega niveles de intensidad que no existen. Rellenar con ceros (`BORDER_CONSTANT`), en cambio, metería píxeles negros artificiales en el histograma de las ventanas del borde y alteraría la ecualización.

*(Fuente: `PI_U2_Transformacion_y_Filtrado_p2.py`, líneas 12–20)*

---

## 3. Código de referencia de la cátedra usado

| Archivo | Carpeta | Qué se tomó |
|---|---|---|
| `PI_U2_Transformacion_y_Filtrado_p1.py` | `U2/Código-20260826` | `cv2.imread(..., IMREAD_GRAYSCALE)`, `cv2.equalizeHist()`, relación histograma → CDF, subplots con `sharex/sharey` y `vmin/vmax`, estilo de comentarios de parámetros (`imadjust`) |
| `PI_U2_Transformacion_y_Filtrado_p2.py` | `U2/Código-20260826` | Tipos de borde de OpenCV y elección de `BORDER_REPLICATE` |
| `PDI_U2_p2_stain.py` | `U2/Ejercicios-20260923` | Ecualizar **un recorte** de la imagen (`img[f1:f2, c1:c2]` + `cv2.equalizeHist`), uso de `pathlib.Path`, validación de carga de la imagen |
| Enunciado `TUIA_PDI_TP1_2026_C2.pdf` | raíz del repo | `cv2.copyMakeBorder` con `cv2.BORDER_REPLICATE` (AYUDA) |

> Nota: `pract2_milyvalen.py` no se tomó como referencia porque es código propio, no de la cátedra.

---

## 4. Resolución: código explicado por bloques

Archivo: `problema1.py`

### Bloque 1: importaciones y validación de la ventana

```python
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
```

- **Concepto:** el enunciado pide M, N ∈ Z⁺, y para que exista un píxel central además tienen que ser impares (ver 2.4).
- **Fuente:** las librerías `cv2`, `numpy` y `matplotlib.pyplot` son las de todos los archivos de la cátedra, por ejemplo `PI_U2_Transformacion_y_Filtrado_p1.py`. El estilo de comentarios de parámetros sale de `imadjust()` en ese mismo archivo. `pathlib.Path` sale de `PDI_U2_p2_stain.py`.
- **Adaptación al TP:** también acepta enteros de NumPy (`np.int64`, etc.), útil para el punto C si los tamaños se generan con `np.arange`.

### Bloque 2: agregar bordes

```python
    m, n = M // 2, N // 2
    img_borde = cv2.copyMakeBorder(img, m, m, n, n, cv2.BORDER_REPLICATE)
```

- **Concepto:** se agregan m filas arriba y abajo y n columnas a los costados para que la ventana nunca se salga de la imagen. `BORDER_REPLICATE` no agrega intensidades nuevas (ver 2.5).
- **Fuente:** la AYUDA del enunciado y los tipos de borde de `PI_U2_Transformacion_y_Filtrado_p2.py`.
- **Adaptación al TP:** M es el alto (top/bottom) y N el ancho (left/right), así que también funcionan ventanas rectangulares.

### Bloque 3: recorrido píxel a píxel y ecualización local

```python
    y = np.zeros_like(img)
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            ventana = img_borde[i:i + M, j:j + N]    # Ventana MxN centrada en (i, j)
            ventana_eq = cv2.equalizeHist(ventana)   # Transformación de ecualización local
            y[i, j] = ventana_eq[m, n]               # Sólo se conserva el píxel central
    return y
```

- **Concepto:** es la sección 2.3 implementada. Por el padding, el píxel (i, j) de la imagen original queda en (i+m, j+n) de `img_borde`. Por eso `img_borde[i:i+M, j:j+N]` es exactamente la ventana centrada en (i, j), y dentro de ella el centro está en `[m, n]`. `cv2.equalizeHist` calcula el histograma de la ventana y le aplica la transformación por CDF. De ese resultado se guarda solo el píxel central.
- **Fuente:**
  - `cv2.equalizeHist()` sale de `PI_U2_Transformacion_y_Filtrado_p1.py` (sección "Ecualización de histograma").
  - Ecualizar un recorte con slicing es lo que hace `PDI_U2_p2_stain.py` para recuperar la zona de la mancha.
- **Adaptación al TP:** en vez de un único recorte fijo como en `PDI_U2_p2_stain.py`, el recorte se desliza píxel a píxel por toda la imagen.

### Bloque 4: ejecución y visualización con varios tamaños de ventana

```python
if __name__ == '__main__':
    ruta = Path(__file__).parent / 'Imagen_con_detalles_escondidos.tif'
    img = cv2.imread(str(ruta), cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError(f'No se pudo cargar la imagen desde {ruta}')

    # Tamaños de ventana a probar (M x N)
    ventanas = [(3, 3), (7, 7), (15, 15), (31, 31), (61, 61)]

    ax1 = plt.subplot(231)
    plt.imshow(img, cmap='gray', vmin=0, vmax=255)
    plt.title('Imagen Original')
    plt.xticks([]), plt.yticks([])

    for k, (M, N) in enumerate(ventanas):
        img_eq_local = ecualizacion_local(img, M, N)
        plt.subplot(2, 3, k + 2, sharex=ax1, sharey=ax1)
        plt.imshow(img_eq_local, cmap='gray', vmin=0, vmax=255)
        plt.title(f'Ecualización local ({M}x{N})')
        plt.xticks([]), plt.yticks([])

    plt.show()
```

- **Concepto:** se carga la imagen en escala de grises (la ecualización trabaja sobre un único canal uint8). La original y los resultados se muestran juntos con ejes compartidos, para hacer zoom en todas a la vez. `vmin=0, vmax=255` evita que matplotlib reescale el contraste automáticamente, lo que confundiría la comparación.
- **Fuente:** `cv2.imread(..., cv2.IMREAD_GRAYSCALE)`, `plt.subplot(..., sharex=ax1, sharey=ax1)` y `vmin/vmax` salen de `PI_U2_Transformacion_y_Filtrado_p1.py`. La validación `if img is None` sale de `PDI_U2_p2_stain.py`.
- **Adaptación al TP:** un `for` recorre los tamaños 3×3, 7×7, 15×15, 31×31 y 61×61 y muestra cada resultado en una grilla 2×3 junto a la original, con ejes compartidos para comparar la misma zona. Es la base para el punto C. `plt.xticks([]), plt.yticks([])` ocultan los ejes, igual que en `PI_U2_Transformacion_y_Filtrado_p2.py`.

---

## 5. Verificación

| Prueba | Resultado |
|---|---|
| Imagen del TP (256×256), ventana 15×15 | Corre sin errores, ~0,14 s; salida uint8 del mismo tamaño |
| Ventanas 3×3, 3×7 (rectangular), 1×1 | Salida del mismo tamaño que la entrada |
| M, N como `np.int64` | Aceptados |
| M par (4×3), M = 0, M = 3.0 (float) | Lanzan `ValueError` |
| Imagen sintética: cuadrado oculto con 5 niveles de diferencia respecto del fondo | Tras la ecualización local la diferencia pasa a 255 |
| Imagen del TP: ecualización global (`cv2.equalizeHist`) vs local | La global casi no cambia nada; la local deja ver el contenido escondido dentro de los 5 cuadrados negros |

La imagen original tiene solo 15 niveles de intensidad distintos: 0–11 (cuadrados negros y lo que tienen adentro) y 226–228 (fondo claro). Por eso la ecualización global no sirve: los detalles difieren en pocos niveles de su entorno y pesan muy poco en el histograma total.

---

## 6. Observaciones

- **Ruido en zonas uniformes:** en el fondo claro aparecen puntitos. Es el comportamiento esperado de la ecualización local: en una ventana casi constante, diferencias de 1–2 niveles se estiran a todo el rango. No es un error del código y conviene analizarlo en el punto C, donde el tamaño de ventana influye directamente.
- **Costo computacional:** se hace una ecualización por píxel, es decir (alto × ancho) llamadas a `equalizeHist`. Para 256×256 son 65.536 llamadas, que corren rápido porque cada ventana es chica.

---

## 7. Entorno

- Entorno virtual en `.venv/` (ignorado por git).
- Dependencias en `requirements.txt`: `numpy`, `opencv-python`, `matplotlib`.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python problema1.py
```

---

## 8. Estado

- [x] **Punto A:** función `ecualizacion_local(img, M, N)`
- [ ] **Punto B:** aplicar a `Imagen_con_detalles_escondidos.tif` e informar los detalles ocultos
- [ ] **Punto C:** analizar la influencia del tamaño de ventana
- [ ] **Problema 2:** validación de planillas de calificaciones
