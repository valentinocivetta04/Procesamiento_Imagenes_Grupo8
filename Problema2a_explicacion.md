# TP1 PDI – Problema 2a: validación de la planilla de calificaciones

Procesamiento de Imágenes I (IA 4.4) · TUIA – FCEIA – UNR · 2026, 2° semestre

El código está en `problema2.py`. Se corre así:

```bash
python problema2.py grade_sheet_2.png
```

Sin argumento usa `grade_sheet_1.png`.

## Qué pide el punto a

El script recibe solo la imagen de una planilla y tiene que mostrar, para cada registro, si cada campo está bien cargado (OK) o no (MAL). Las reglas salen del enunciado (`TUIA_PDI_TP1_2026_C2.pdf`, Problema 2):

| Campo | Regla |
|---|---|
| Legajo | 8 caracteres, una sola palabra |
| Nombre y apellido | al menos 2 palabras y como mucho 12 caracteres |
| Parcial 1, 2 y 3 | 1 o 2 caracteres seguidos, sin espacios |
| Condición Final | un solo caracter |

No hay que leer qué dice cada campo. Alcanza con contar caracteres y palabras, que es justamente lo que se puede sacar de la imagen con lo visto en la materia.

## Cómo lo resolvimos

### 1. Binarizar la imagen

Pasamos la planilla a escala de grises y armamos una matriz booleana con `img < 150`: el texto y las líneas de la tabla quedan en True y el fondo en False.

- De dónde sale: la AYUDA del enunciado (`img_th = img < th`), el umbral manual de `U3/Código-20260923/PDI_U3_Segmentacion.py` (sección "Umbralado") y la matriz booleana `gray_image < 5` de `U2/Ejercicios-20260923/PDI_U2_p2_stain.py`.
- Por qué 150: lo elegimos mirando los valores de la imagen, igual que el `th = 100` manual de la cátedra. Los bordes grises de la hoja valen entre 178 y 201, así que con 150 no se cuelan como si fueran líneas de la tabla. El texto y las líneas son casi negros.

### 2. Encontrar las líneas horizontales

Sumamos los True de cada fila (`np.sum(img_th, 1)`). Las filas donde hay una línea de la tabla tienen muchísimos más píxeles oscuros que el resto, así que nos quedamos con las que superan el 80 % del máximo.

- De dónde sale: la AYUDA del enunciado (`img_rows = np.sum(img_th_ones, 1)` y `img_rows > th_row`) y `PDI_U2_p2_stain.py`, que usa `np.sum(boolean_matrix, axis = 1)` y compara contra `sum_rows.max()` para encontrar las líneas del texto.
- Por qué relativo al máximo: las cuatro planillas tienen tamaños distintos (1107, 1029, 1106 y 917 px de ancho), así que un umbral fijo en píxeles no sirve para todas. La línea que está debajo de "Notas" es más corta que las demás y queda afuera, que es lo que queremos.

Con ese vector booleano hay que pasar de "filas en True" a "dónde empieza y dónde termina cada línea". Para eso usamos la técnica de pulsos: `np.diff` marca los cambios, `np.argwhere` da sus índices, a los inicios se les suma 1 y se agrupan de a pares con `reshape(-1, 2)`.

- De dónde sale: `U1/PDI_U1_p1_Letras.py`, sección "EJEMPLO: Encontrar inicio/fin de pulsos" y el armado de `r_idxs` en la PARTE 1 (detección de renglones). La AYUDA del TP avisa que las líneas pueden tener más de un píxel de ancho y que hay que encontrar su principio y su fin, y esta técnica resuelve eso.

En las cuatro planillas aparecen 22 líneas: el borde de arriba de la tabla, la línea debajo del encabezado y una debajo de cada uno de los 20 registros. Cada registro queda entre dos líneas seguidas, a partir de la segunda.

### 3. Encontrar las líneas verticales

Hacemos lo mismo con las columnas (`np.sum(..., 0)`), pero solo en la zona de los registros, entre la línea de abajo del encabezado y la última línea. Si sumáramos toda la altura, las divisiones entre Parcial 1, 2 y 3 quedarían más cortas que el resto (arrancan en el sub-encabezado) y el logo y el título meterían ruido. Recortando esa zona, todas las líneas verticales tienen el mismo largo y el umbral del 80 % las toma a las 8.

- De dónde sale: la AYUDA del TP (`img_cols = np.sum(img_th_ones, 0)`) y `PDI_U2_p2_stain.py`, que primero recorta la franja horizontal y después busca los límites por columnas.

Las 8 líneas definen 7 columnas. La primera es "Nro." y no se valida.

### 4. Recortar cada celda

Cada celda es el rectángulo entre dos líneas horizontales y dos verticales seguidas, sin incluir las líneas: desde el fin de una línea + 1 hasta el inicio de la siguiente. Es el mismo recorte por índices `img[ini:fin, :]` que se usa en `PDI_U1_p1_Letras.py` para sacar cada renglón y cada letra.

### 5. Contar caracteres

Sobre cada celda aplicamos `cv2.connectedComponentsWithStats(celda, 8, cv2.CV_32S)`. Cada caracter es una componente conectada.

- De dónde sale: `PDI_U3_Segmentacion.py`, sección "Componentes conectadas" (misma llamada, conectividad 8, y la explicación de `stats` como bounding box + área), y la segunda AYUDA del TP.
- El primer elemento de `stats` es el fondo (etiqueta 0), así que lo sacamos. En el ejemplo de la cátedra se ve porque el primer bounding box que se dibuja encierra toda la imagen.
- Después filtramos por área con `stats[:, -1] > th_area`, como sugiere la AYUDA. Usamos `th_area = 1`, o sea que solo descartamos píxeles sueltos. Como la celda se recorta sin las líneas no quedan restos de la tabla, y un umbral más alto se comía caracteres reales: el guion mide entre 4 y 5 px de área y el punto de "1.0" mide 3.

### 6. Contar palabras

Ordenamos las componentes de izquierda a derecha (con `sorted(..., key=...)`, como en la sección "Ordeno según los contornos mas grandes" de `PDI_U3_Segmentacion.py`) y medimos cuántas columnas vacías hay entre el final de un caracter y el comienzo del siguiente. Si hay más de 6 px, hay un espacio. Palabras = espacios + 1.

- De dónde sale la idea: `PDI_U1_p1_Letras.py` separa las letras de un renglón buscando las columnas vacías entre ellas. Acá hacemos lo mismo un nivel más arriba: las columnas vacías cortas separan letras y las largas separan palabras.
- De dónde sale el 6: lo medimos en las cuatro planillas. Entre letras de una misma palabra hay de 0 a 4 px, y un espacio mide de 10 a 13 px. El 6 queda cómodo en el medio.

### 7. Aplicar las reglas e imprimir

Con la cantidad de caracteres y de palabras de cada celda se aplica la regla de su campo y se imprime OK o MAL, con el formato del ejemplo del enunciado (`> Registro 1:`, `> Legajo: OK`, ...).

## Verificación

Corrimos el script sobre las cuatro planillas y comparamos a mano los 80 registros con lo que se ve en cada imagen. Coinciden todos. Algunos casos que confirman que las reglas funcionan:

| Planilla | Registro | Contenido | Resultado |
|---|---|---|---|
| 1 | 1 | Ejemplo de la figura 3a (C-1557/1, JUAN CARLINI, 6, 6, 7, A) | todo OK |
| 2 | 1 | JULIAN CARLINI (13 letras) | Nombre MAL |
| 2 | 4 | R-87455/6 (9 caracteres) | Legajo MAL |
| 2 | 19 | S-94722/ 1 (tiene un espacio) | Legajo MAL; Parcial 3 = 100, MAL |
| 3 | 8 | AMANDASANTOS (una sola palabra) | Nombre MAL |
| 3 | 15 | Parcial 2 = 1.0 (el punto cuenta como caracter) | Parcial 2 MAL |
| 2 | 17 | Condición "Rec" | Condición MAL |
| 1 | 3, 11, 14, 15, 20 | Filas vacías | todo MAL (ningún campo cumple su regla) |

## Cosas que decidimos nosotros (el material no las define)

- **Los 12 caracteres del nombre no cuentan el espacio.** El enunciado dice "no más de 12 caracteres en total" pero no aclara si el espacio suma. Contando componentes conectadas el espacio no aparece (no tiene píxeles), así que contamos solo letras. Con esa interpretación AMANDA SANTOS (12 letras) da OK. Si la cátedra quiere contar el espacio, alcanza con sumar `n_pal - 1` a los caracteres.
- **Una fila vacía da todo MAL.** Ningún campo vacío cumple su regla, así que es lo que sale de aplicar el enunciado tal cual.
- **La Ñ se contaría como dos caracteres** (la N y la tilde son dos componentes). En las planillas no aparece ninguna, así que no lo resolvimos. Si hiciera falta, habría que unir las componentes que se superponen en x.
- **Los umbrales (150, 80 % del máximo, área 1, espacio 6 px)** no salen de ningún archivo. La AYUDA dice que hay que "definir un umbral acorde", y estos los ajustamos mirando las cuatro planillas.

## Próximos pasos (Parte 2, puntos b, c y d)

Esto es solo el enfoque. Todavía no está implementado.

Para los tres puntos conviene que `validar_planilla` además de imprimir devuelva los resultados de cada registro (la lista de OK/MAL y las coordenadas de la celda del nombre). Así b, c y d reutilizan lo del punto a sin volver a procesar la imagen.

### Punto b: imagen con los alumnos que no aprobaron

1. Quedarse con los registros que tienen los seis campos en OK.
2. De esos, ver qué letra hay en Condición Final. Acá aparece algo nuevo: en el punto a solo contamos caracteres y ahora hay que distinguir L, R y A. Una forma de hacerlo con lo que vimos es la jerarquía de contornos de `cv2.findContours` con `RETR_TREE` (`PDI_U3_Segmentacion.py`, secciones "Contornos que no tienen madres/padres" e "hijas/os"). La L no tiene agujeros y la A y la R tienen uno. Para separar A de R habría que buscar otra diferencia de forma, por ejemplo el área o el bounding box de la componente (`stats`). Hay que probarlo con las letras de las planillas antes de decidir.
3. Recortar la celda de Nombre y apellido de cada alumno con L o R (ya tenemos sus coordenadas del punto a).
4. Armar una sola imagen con todos los recortes y marcar cada uno según su condición: un rectángulo de color distinto con `cv2.rectangle` (como en la sección de componentes conectadas de `PDI_U3_Segmentacion.py`) o un texto con `cv2.putText` (como en `U2/Código-20260826/PI_U2_ej_video_face_detection_and_blur.py`).

### Punto c: archivo CSV

1. Una fila por registro, con el ID (número de registro, en el mismo orden que la planilla) en la primera columna.
2. Después, las columnas Legajo, Nombre y Apellido, Parcial 1, Parcial 2, Parcial 3 y Condición Final, con OK o MAL.
3. El material de la cátedra no tiene ningún ejemplo de CSV. Lo más simple sería el módulo `csv` de la biblioteca estándar de Python. Lo aviso porque es la única herramienta que no sale de la carpeta.

### Punto d: correr todo sobre las cuatro planillas

1. Recorrer los archivos `grade_sheet_<id>.png` con un `for`, llamar a la validación con cada uno y generar su salida de consola, su imagen (punto b) y su CSV (punto c) con nombres que incluyan el id, parecido a cómo `PDI_U1_p1_Letras.py` genera un archivo por letra (MEJORA 2).
2. Informar los resultados: cuántos registros y campos dieron OK y MAL en cada planilla y qué alumnos quedaron en L o R.

## Fuentes usadas

| Archivo | Qué se tomó |
|---|---|
| `TUIA_PDI_TP1_2026_C2.pdf` (en el repo del grupo) | Reglas de cada campo, formato de salida, AYUDAS: umbral, sumas por fila/columna, líneas de más de 1 px, componentes conectadas y filtrado por área |
| `U1/PDI_U1_p1_Letras.py` | Inicio/fin de pulsos con `np.diff` + `np.argwhere`, agrupar de a pares con `reshape`, recortes por índices, separar letras por columnas vacías |
| `U2/Ejercicios-20260923/PDI_U2_p2_stain.py` | Matriz booleana por umbral, `np.sum` por filas y columnas comparando contra el máximo, recortar una franja y después buscar por columnas |
| `U3/Código-20260923/PDI_U3_Segmentacion.py` | Umbralado manual, `cv2.connectedComponentsWithStats` y significado de `stats`, ordenar con `sorted(..., key=...)`. Para el punto b: `findContours` con jerarquía y `cv2.rectangle` |
| `U2/Código-20260826/PI_U2_ej_video_face_detection_and_blur.py` | `cv2.putText`, solo para el punto b |
