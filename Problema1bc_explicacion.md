# TP1 PDI – Problema 1b y 1c: detalles ocultos e influencia del tamaño de ventana

Procesamiento de Imágenes I (IA 4.4) · TUIA – FCEIA – UNR · 2026, 2° semestre

Continúa a `Problema1a_explicacion.md`. Todo el código está en `problema1.py`.

---

## 1. Qué pide el enunciado

> **b.** Utilice la función desarrollada en el punto anterior para analizar la imagen de la figura 1 e informe cuáles son los detalles ocultos presentes en las diferentes zonas de la imagen.
>
> **c.** Realice un análisis sobre la influencia del tamaño de la ventana en los resultados obtenidos, utilizando diferentes tamaños de ventana.

---

## 2. Cómo es la imagen original

`Imagen_con_detalles_escondidos.tif` es de 256×256 (uint8) y tiene sólo 15 niveles de gris distintos:

| Región | Niveles | Píxeles |
|---|---|---|
| Fondo claro | 226, 227, 228 | 1175 / 43946 / 1195 |
| 5 cuadrados oscuros de 62×62 px | 0 a 11 | 5 × 3844 |

El fondo claro no es totalmente uniforme: tiene píxeles sueltos de 226 y 228 sobre un fondo de 227. Adentro de cada cuadrado el fondo es 0 (con algunos píxeles sueltos de nivel 1) y el detalle está dibujado con niveles entre 1 y 11. Como la diferencia es de 5 a 10 niveles sobre 255, a simple vista no se ve nada.

**Por qué falla la ecualización global:** los 19.220 píxeles oscuros (niveles 0 a 11) ocupan el 29 % de la imagen y quedan juntos al principio de la CDF. Al ecualizar, casi todos se mapean a valores muy bajos. El contraste medio entre detalle y fondo del cuadrado queda en **7,2 niveles**, así que los detalles siguen sin verse.

---

## 3. Punto B: detalles ocultos

### 3.1 Procedimiento

1. **Detectar las zonas** (`detectar_zonas`): se umbraliza con `img < 128` y se buscan las componentes conectadas con `cv2.connectedComponentsWithStats`. Las componentes con área > 100 px son los 5 cuadrados. Se ordenan de arriba hacia abajo y de izquierda a derecha.
2. **Ecualizar localmente** toda la imagen con la ventana elegida en el punto C: **21×21**.
3. **Mostrar** la imagen completa (original, global y local) y un zoom de cada zona antes y después (figuras 1 y 2 del script).
4. **Medir** cada detalle (`medir_detalle`): se umbraliza el recorte ecualizado con `> 128`, se sacan las componentes de menos de 10 px (ruido) y se informa cuántos objetos quedan y el tamaño del rectángulo que los contiene. Es el mismo filtrado por área que sugiere la AYUDA del Problema 2 (`stats[:, -1] > th_area`).

### 3.2 Resultado

| Zona | Posición (x, y) | Niveles originales | Objetos | Tamaño | Detalle oculto |
|---|---|---|---|---|---|
| Superior izquierda | (6, 6) | 0..11 | 1 | 14×14 px | **Un cuadrado pequeño**, centrado |
| Superior derecha | (187, 6) | 0..7 | 1 | 29×29 px | **Una línea diagonal**, de abajo a la izquierda hacia arriba a la derecha |
| Centro | (97, 97) | 0..6 | 1 | 19×22 px | **La letra "a" minúscula** |
| Inferior izquierda | (6, 188) | 0..9 | 4 | 42×34 px | **Cuatro líneas horizontales paralelas**, de unos 2 px de grosor y separadas unos 11 px |
| Inferior derecha | (187, 188) | 0..11 | 1 | 33×33 px | **Un círculo** relleno |

Salida de consola:

```
--- Punto B: detalles ocultos (ventana 21x21) ---
> Zona Superior izquierda  (x=  6, y=  6, 62x62 px) | niveles originales 0..11 | 1 objeto(s), 14x14 px | Un cuadrado pequeño
> Zona Superior derecha    (x=187, y=  6, 62x62 px) | niveles originales 0..7 | 1 objeto(s), 29x29 px | Una línea diagonal (de abajo-izq. hacia arriba-der.)
> Zona Centro              (x= 97, y= 97, 62x62 px) | niveles originales 0..6 | 1 objeto(s), 19x22 px | La letra "a" minúscula
> Zona Inferior izquierda  (x=  6, y=188, 62x62 px) | niveles originales 0..9 | 4 objeto(s), 42x34 px | Cuatro líneas horizontales paralelas
> Zona Inferior derecha    (x=187, y=188, 62x62 px) | niveles originales 0..11 | 1 objeto(s), 33x33 px | Un círculo
```

> Nota: la descripción del detalle (`DETALLES_OBSERVADOS`) sale de mirar las imágenes. Lo que el script calcula solo es la ubicación de las zonas, los niveles, la cantidad de objetos y su tamaño, y eso confirma lo que se ve (por ejemplo, las 4 componentes de las líneas horizontales).

---

## 4. Punto C: influencia del tamaño de la ventana

### 4.1 Cómo se midió

Además de comparar las imágenes a ojo (figuras 3, 4 y 5 del script), se usaron tres medidas para cada ventana (figura 6 y tabla por consola):

- **Contraste por zona** (`contraste_por_zona`): media del detalle − media del fondo del cuadrado, en la imagen procesada. Las máscaras salen de la imagen **original** (`mascaras_referencia`): detalle = píxeles > 0 luego de un filtro de mediana 3×3 (así se descartan los píxeles de ruido del fondo del cuadrado); el fondo del cuadrado se toma alejado 2 px del detalle, usando `cv2.blur(mascara, (5, 5)) > 0` para "agrandar" la máscara. Va de 0 (no se distingue) a 255 (blanco sobre negro).
- **Ruido en el fondo claro** (`ruido_fondo`): % de píxeles del fondo claro que quedaron oscuros (< 128).
- **Tiempo** de ejecución de `ecualizacion_local`.

### 4.2 Resultados

```
  Ventana | Contraste medio | Sup. izq. | Sup. der. |    Centro | Inf. izq. | Inf. der. | Ruido fondo | Tiempo
   3x3    |           152.3 |     111.4 |     163.9 |     166.3 |     238.8 |      81.5 |       17.6% |  0.11s
   5x5    |           181.3 |     206.9 |     163.0 |     164.8 |     239.1 |     132.6 |       27.7% |  0.10s
   7x7    |           195.3 |     233.6 |     162.4 |     167.7 |     240.7 |     172.0 |       23.3% |  0.11s
   9x9    |           201.1 |     234.4 |     163.1 |     169.2 |     242.5 |     196.5 |       14.6% |  0.11s
  15x15   |           205.6 |     236.1 |     165.3 |     171.0 |     244.7 |     210.7 |        2.9% |  0.13s
  21x21   |           199.5 |     237.7 |     168.0 |     172.1 |     209.0 |     210.9 |        2.5% |  0.17s
  31x31   |           192.3 |     239.8 |     173.6 |     174.0 |     163.6 |     210.5 |        2.5% |  0.28s
  45x45   |           166.3 |     241.9 |     137.8 |     170.2 |      93.8 |     187.7 |        2.5% |  0.40s
  61x61   |            82.8 |     118.6 |      49.5 |      73.5 |      46.1 |     126.0 |        2.5% |  0.67s
  81x81   |            27.4 |      24.4 |      10.9 |      22.1 |      21.3 |      58.6 |        2.5% |  1.00s
 101x101  |            13.6 |      10.7 |       4.9 |      10.3 |      11.2 |      31.0 |        2.5% |  1.51s
   3x31   |           205.7 |     237.2 |     176.8 |     172.0 |     232.0 |     210.4 |        9.6% |  0.11s
  31x3    |           194.3 |     235.3 |     175.8 |     174.1 |     175.5 |     211.1 |       10.2% |  0.12s
   1x61   |           160.4 |     203.7 |      87.2 |     134.1 |     196.4 |     180.7 |       15.6% |  0.11s
  61x1    |           138.3 |     201.1 |      88.7 |     138.8 |      82.7 |     180.4 |       14.3% |  0.16s
   Global |             7.2 |      11.8 |       4.3 |       4.3 |       4.9 |      10.9 |        2.5% |
```

*(Los tiempos varían según la computadora.)*

### 4.3 Análisis

**Ventanas muy chicas (3×3 a 9×9): resaltan bordes y amplifican el ruido.**

- Con 3×3 los detalles grandes aparecen **huecos**: sólo se ve el contorno del cuadrado pequeño y del círculo (contraste 111 y 81). Cuando la ventana cae entera adentro del detalle, todos sus píxeles tienen casi el mismo nivel y no hay nada que estirar. Sólo en el borde, donde la ventana mezcla detalle y fondo, aparece contraste. Los detalles finos (líneas de 2 px, la "a") sí se ven bien porque la ventana siempre toca el borde.
- El fondo claro se llena de ruido (hasta un 27,7 % de píxeles oscurecidos con 5×5). En una ventana del fondo hay sólo 227 y 228, o sólo 226 y 227: `cv2.equalizeHist` lleva el nivel más bajo presente a 0 y una diferencia de 1 nivel pasa a ser negro contra blanco. Con 5×5 a 9×9 se forman manchas negras grandes.
- A medida que la ventana crece hasta 9×9, el interior de los detalles se va rellenando y el contraste sube.

**Ventanas intermedias (15×15 a 31×31): el mejor resultado.**

- Los 5 detalles se ven completos y nítidos. El contraste medio queda cerca de 200.
- El ruido del fondo baja al mínimo (2,5 %). Casi todas las ventanas incluyen algún píxel de 226, que es siempre el nivel más bajo del fondo. Ese 2,5 % son justamente los 1175 píxeles de 226 que tiene la imagen original: son ruido de la imagen, no del método, y aparecen oscuros incluso con la ecualización global.
- Se eligió **21×21** para el punto B porque el ruido ya está en el mínimo, el contraste es alto en todas las zonas y dentro de los cuadrados quedan menos puntos sueltos que con 15×15.

**Ventanas grandes (45×45 en adelante): el resultado se parece al de la ecualización global.**

- El contraste cae fuerte: 166 → 83 → 27 → 14 (con 101×101 ya se parece al global, 7,2).
- **Por qué:** cuando la ventana se sale del cuadrado de 62×62, entran píxeles del fondo claro (226–228). En la CDF de la ventana, esos píxeles ocupan la parte de arriba. Todos los niveles oscuros (0 a 11) quedan comprimidos en `[0, 255·p]`, donde `p` es la fracción de píxeles oscuros en la ventana. Cuanto más grande es la ventana, más chico es `p` y más oscuro queda el detalle.
- **Cada zona empieza a perder contraste cuando la mitad de la ventana (M//2) es mayor que la distancia del detalle al borde de su cuadrado**, aproximadamente:

| Zona | Distancia detalle → borde del cuadrado | Primera ventana donde cae el contraste |
|---|---|---|
| Inferior izquierda (líneas) | ~10 px | 21×21 (m = 10) |
| Superior derecha (línea) | ~16 px | 45×45 (m = 22) |
| Inferior derecha (círculo) | ~13 px | 45×45 (m = 22) |
| Centro ("a") | ~19 px | 61×61 (m = 30) |
| Superior izquierda (cuadrado) | ~24 px | 61×61 (m = 30) |

- Con 61×61 aparece un efecto de **viñeta**: el centro del detalle queda más claro que los bordes, porque la ventana centrada en el borde del detalle incluye más fondo claro.

**Ventanas rectangulares: la orientación importa.**

- Con **3×31** (ventana horizontal) las líneas horizontales se mantienen nítidas (232). Con **31×3** (ventana vertical) se degradan (175): la ventana vertical sale del cuadrado por arriba y por abajo y toma fondo claro.
- Con **1×61** y **61×1** el problema es mayor: la ventana sale del cuadrado en una dirección y comprime los detalles, sobre todo la línea diagonal (87–89).
- En el fondo aparece ruido en forma de **rayas** orientadas como la ventana (horizontales con 3×31, verticales con 31×3).
- Conclusión: si el detalle tiene una dirección conocida, conviene una ventana alargada en esa misma dirección. Si no se sabe, lo más seguro es una ventana cuadrada.

**Costo computacional.**

- El tiempo crece con el tamaño de la ventana (0,1 s con 3×3 a 1,5 s con 101×101 para una imagen de 256×256), porque en cada píxel se calcula el histograma de M·N valores. Para ventanas chicas domina el costo del recorrido píxel a píxel.

### 4.4 Conclusión

El tamaño de ventana tiene que estar **entre dos límites** que dependen de la imagen:

- **Mínimo:** lo bastante grande para que, en casi cualquier posición, la ventana tome a la vez parte del detalle y parte de su fondo. Si no, sólo se ven bordes y el ruido del fondo se amplifica.
- **Máximo:** lo bastante chica para no salirse de la zona donde está el detalle. Si no, el fondo claro vuelve a dominar el histograma y el resultado se acerca al de la ecualización global.

En esta imagen el rango útil está entre **15×15 y 31×31**, y 21×21 da el mejor equilibrio.

---

## 5. Código agregado a `problema1.py`

| Función / bloque | Punto | Qué hace |
|---|---|---|
| `detectar_zonas(img, th, area_min)` | B | Umbral + `cv2.connectedComponentsWithStats` para ubicar los 5 cuadrados |
| `medir_detalle(zona_eq, th, area_min)` | B | Cuenta objetos y mide el tamaño del detalle ya ecualizado |
| `mascaras_referencia(img, zonas)` | C | Máscaras de detalle, fondo del cuadrado y fondo claro, a partir de la original |
| `contraste_por_zona(...)` | C | Media del detalle − media del fondo del cuadrado |
| `ruido_fondo(...)` | C | % del fondo claro que quedó oscuro |
| `__main__` – Punto B | B | Figuras 1 y 2 + informe por consola |
| `__main__` – Punto C | C | Tabla por consola + figuras 3 a 6 |

Figuras que genera el script:

1. **Punto B – Global vs. local:** original, ecualización global y ecualización local 21×21.
2. **Punto B – Detalles por zona:** zoom de cada cuadrado antes y después.
3. **Punto C – Ventanas cuadradas:** imagen completa con 3, 7, 15, 21, 31, 61 y 101.
4. **Punto C – Zonas vs. tamaño de ventana:** grilla de zonas (columnas) por ventana (filas).
5. **Punto C – Ventanas rectangulares:** 3×31, 31×3, 1×61 y 61×1.
6. **Punto C – Medidas:** contraste por zona, ruido del fondo y tiempo en función del lado de la ventana.

**Fuentes de la cátedra:** `cv2.equalizeHist`, subplots con `sharex/sharey` y `vmin/vmax` (`PI_U2_Transformacion_y_Filtrado_p1.py`), filtro de mediana y `cv2.blur` (Unidad 2, filtrado espacial), y `cv2.connectedComponentsWithStats` con filtrado por área (AYUDA del Problema 2 del enunciado).

---

## 6. Estado

- [x] **Punto A:** función `ecualizacion_local(img, M, N)`
- [x] **Punto B:** detalles ocultos: cuadrado pequeño, línea diagonal, letra "a", cuatro líneas horizontales y círculo
- [x] **Punto C:** análisis del tamaño de ventana (cuadradas y rectangulares)
- [ ] **Problema 2:** validación de planillas de calificaciones
