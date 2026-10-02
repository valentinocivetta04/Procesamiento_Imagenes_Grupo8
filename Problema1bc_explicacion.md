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

**Por qué falla la ecualización global:** los 19.220 píxeles oscuros (niveles 0 a 11) ocupan el 29 % de la imagen y quedan juntos al principio de la CDF. Al ecualizar, casi todos se mapean a valores muy bajos y los detalles siguen sin verse (figura 1 del script).

---

## 3. Punto B: detalles ocultos

### 3.1 Procedimiento

1. **Ubicar las zonas:** las coordenadas de los 5 cuadrados (62×62 px) las medimos a mano sobre la imagen. Están en la tabla `ZONAS` del script, junto con el detalle que se ve en cada una. El enunciado pide analizar una sola imagen, así que no hace falta detectarlas automáticamente.
2. **Ecualizar localmente** toda la imagen con la ventana elegida en el punto C: **21×21**.
3. **Mostrar** la imagen completa (original, global y local) y un zoom de cada zona antes y después (figuras 1 y 2 del script).
4. **Informar** por consola el detalle de cada zona.

### 3.2 Resultado

| Zona | Posición (x, y) | Detalle oculto |
|---|---|---|
| Superior izquierda | (6, 6) | **Un cuadrado pequeño**, centrado |
| Superior derecha | (187, 6) | **Una línea diagonal**, de abajo a la izquierda hacia arriba a la derecha |
| Centro | (97, 97) | **La letra "a" minúscula** |
| Inferior izquierda | (6, 188) | **Cuatro líneas horizontales paralelas** |
| Inferior derecha | (187, 188) | **Un círculo** relleno |

Salida de consola:

```
--- Punto B: detalles ocultos (ventana 21x21) ---
> Superior izquierda: Un cuadrado pequeño
> Superior derecha: Una línea diagonal (de abajo-izq. hacia arriba-der.)
> Centro: La letra "a" minúscula
> Inferior izquierda: Cuatro líneas horizontales paralelas
> Inferior derecha: Un círculo
```

> Nota: la descripción de cada detalle sale de mirar la figura 2. El script no la calcula: la muestra como título de cada recorte y la imprime.

---

## 4. Punto C: influencia del tamaño de la ventana

### 4.1 Cómo se analizó

Comparamos a ojo las imágenes ecualizadas con distintas ventanas:

- **Figura 3:** imagen completa con ventanas cuadradas de 3, 7, 15, 21, 31, 61 y 101, junto a la original y a la ecualización global.
- **Figura 4:** ventanas rectangulares de 3×31, 31×3, 1×61 y 61×1, con la de 21×21 como referencia.

Las dos figuras comparten los ejes (`sharex`/`sharey`, como en el código de la cátedra), así que al hacer zoom sobre una zona se ve la misma región con todas las ventanas.

### 4.2 Análisis

**Ventanas muy chicas (3×3 y 7×7): resaltan bordes y amplifican el ruido.**

- Con 3×3 los detalles grandes aparecen **huecos**: sólo se ve el contorno del cuadrado pequeño y del círculo. Cuando la ventana cae entera adentro del detalle, todos sus píxeles tienen casi el mismo nivel y no hay nada que estirar. Sólo en el borde, donde la ventana mezcla detalle y fondo, aparece contraste. Los detalles finos (líneas de 2 px, la "a") sí se ven bien porque la ventana siempre toca el borde.
- El fondo claro se llena de ruido. En una ventana del fondo hay sólo 227 y 228, o sólo 226 y 227: `cv2.equalizeHist` lleva el nivel más bajo presente a 0 y una diferencia de 1 nivel pasa a ser negro contra blanco. Con 7×7 se forman manchas negras grandes.
- A medida que la ventana crece, el interior de los detalles se va rellenando.

**Ventanas intermedias (15×15 a 31×31): el mejor resultado.**

- Los 5 detalles se ven completos y nítidos.
- En el fondo quedan solo puntos negros sueltos. Casi todas las ventanas incluyen algún píxel de 226, que es siempre el nivel más bajo del fondo. Esos puntos son los 1175 píxeles de 226 que tiene la imagen original (el 2,5 % del fondo): son ruido de la imagen, no del método, y aparecen oscuros incluso con la ecualización global.
- Se eligió **21×21** para el punto B porque el fondo ya no tiene manchas, los cinco detalles se ven bien y dentro de los cuadrados quedan menos puntos sueltos que con 15×15.

**Ventanas grandes (61×61 en adelante): el resultado se parece al de la ecualización global.**

- Los detalles se van apagando: con 61×61 ya se ven grises y con 101×101 casi no se distinguen, como en la ecualización global.
- **Por qué:** cuando la ventana se sale del cuadrado de 62×62, entran píxeles del fondo claro (226–228). En la CDF de la ventana, esos píxeles ocupan la parte de arriba. Todos los niveles oscuros (0 a 11) quedan comprimidos en `[0, 255·p]`, donde `p` es la fracción de píxeles oscuros en la ventana. Cuanto más grande es la ventana, más chico es `p` y más oscuro queda el detalle.
- **Cada zona empieza a apagarse cuando la mitad de la ventana (M//2) es mayor que la distancia del detalle al borde de su cuadrado.** Por eso las cuatro líneas de abajo a la izquierda, que están a unos 10 px del borde, ya se ven más apagadas con 31×31. El cuadrado pequeño, a unos 24 px del borde, se sigue viendo bien con 31×31 y recién se apaga con 61×61.
- Con 61×61 aparece un efecto de **viñeta**: el centro del detalle queda más claro que los bordes, porque la ventana centrada en el borde del detalle incluye más fondo claro.

**Ventanas rectangulares: la orientación importa.**

- Con **3×31** (ventana horizontal) las líneas horizontales se mantienen nítidas. Con **31×3** (ventana vertical) se degradan: la ventana vertical sale del cuadrado por arriba y por abajo y toma fondo claro.
- Con **1×61** y **61×1** el problema es mayor: la ventana sale del cuadrado en una dirección y apaga los detalles, sobre todo la línea diagonal.
- En el fondo aparece ruido en forma de **rayas** orientadas como la ventana (horizontales con 3×31, verticales con 31×3).
- Conclusión: si el detalle tiene una dirección conocida, conviene una ventana alargada en esa misma dirección. Si no se sabe, lo más seguro es una ventana cuadrada.

**Costo computacional.**

- El tiempo crece con el tamaño de la ventana, porque en cada píxel se calcula el histograma de M·N valores. Para ventanas chicas domina el costo del recorrido píxel a píxel.

### 4.3 Conclusión

El tamaño de ventana tiene que estar **entre dos límites** que dependen de la imagen:

- **Mínimo:** lo bastante grande para que, en casi cualquier posición, la ventana tome a la vez parte del detalle y parte de su fondo. Si no, sólo se ven bordes y el ruido del fondo se amplifica.
- **Máximo:** lo bastante chica para no salirse de la zona donde está el detalle. Si no, el fondo claro vuelve a dominar el histograma y el resultado se acerca al de la ecualización global.

En esta imagen el rango útil está entre **15×15 y 31×31**, y 21×21 da el mejor equilibrio.

---

## 5. Código agregado a `problema1.py`

| Función / bloque | Punto | Qué hace |
|---|---|---|
| Tabla `ZONAS` | B | Nombre, posición (medida a mano) y detalle observado de cada cuadrado |
| `__main__` – Punto B | B | Figuras 1 y 2 + detalle de cada zona por consola |
| `__main__` – Punto C | C | Figuras 3 y 4 |

Figuras que genera el script:

1. **Punto B – Global vs. local:** original, ecualización global y ecualización local 21×21.
2. **Punto B – Detalles por zona:** zoom de cada cuadrado antes y después.
3. **Punto C – Ventanas cuadradas:** imagen completa con 3, 7, 15, 21, 31, 61 y 101.
4. **Punto C – Ventanas rectangulares:** 3×31, 31×3, 1×61 y 61×1.

**Fuentes de la cátedra:** `cv2.equalizeHist` (`img_heq = cv2.equalizeHist(img)`), subplots con `sharex/sharey` y `vmin/vmax` (`PI_U2_Transformacion_y_Filtrado_p1.py` y diapositivas de U2, p.13 y 14).

---

## 6. Estado

- [x] **Punto A:** función `ecualizacion_local(img, M, N)`
- [x] **Punto B:** detalles ocultos: cuadrado pequeño, línea diagonal, letra "a", cuatro líneas horizontales y círculo
- [x] **Punto C:** análisis del tamaño de ventana (cuadradas y rectangulares)
- [ ] **Problema 2:** validación de planillas de calificaciones
