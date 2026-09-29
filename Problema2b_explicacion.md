# TP1 PDI – Problema 2b: imagen con los alumnos que no aprobaron

Procesamiento de Imágenes I (IA 4.4) · TUIA – FCEIA – UNR · 2026, 2° semestre

El código sigue en `problema2.py`, a continuación del punto a. Se corre igual que antes:

```bash
python problema2.py grade_sheet_1.png
```

Primero imprime la validación del punto a y después guarda la imagen del punto b al lado de la planilla, con el nombre `no_aprobados_grade_sheet_1.png`.

## Qué pide el punto b

Del enunciado (`TUIA_PDI_TP1_2026_C2.pdf`, Problema 2, punto b): una sola imagen de salida con los alumnos que no aprobaron, es decir con Condición Final "L" o "R". Solo cuentan los registros cargados correctamente, y de cada alumno va el recorte del campo Nombre y Apellido con algún indicador que diferencie a los que recuperan (R) de los libres (L).

## Cómo lo resolvimos

### 1. Reusar el punto a

Cambiamos `validar_planilla` para que, además de imprimir, devuelva la imagen, las líneas de la tabla y la lista de OK/MAL de cada registro. Con eso filtramos los registros que tienen los seis campos en OK y no hace falta volver a buscar las celdas. También sacamos el recorte de celdas a una función chica (`celda`) porque ahora se usa en los dos puntos. La salida por consola del punto a no cambió: la comparamos con la de antes en las cuatro planillas y es idéntica.

### 2. Distinguir L, R y A

Este es el problema nuevo. En el punto a solo contábamos caracteres, y ahora hay que saber qué letra hay en Condición Final. En el material no hay nada para reconocer letras, así que usamos dos propiedades de forma que sí se pueden medir con lo que vimos.

La primera es la columna izquierda de la letra. La L y la R arrancan con un trazo vertical, así que la primera columna de su bounding box está llena de arriba a abajo. La A arranca en diagonal y en esa columna tiene muy pocos píxeles. Para medirlo sumamos por columnas la letra recortada a su bounding box y miramos si la primera suma es igual al alto.

- La suma por columnas es la misma de la AYUDA del TP (`np.sum(img_th_ones, 0)`) y de `U2/Ejercicios-20260923/PDI_U2_p2_stain.py`.
- El bounding box sale de `stats` de `cv2.connectedComponentsWithStats` (`U3/Código-20260923/PDI_U3_Segmentacion.py`, sección "Componentes conectadas").

La segunda es si la letra tiene agujero. La R tiene uno (la panza cerrada) y la L no. Usamos `cv2.findContours` con `cv2.RETR_TREE`, que devuelve la jerarquía `[Next, Previous, First_Child, Parent]`. El contorno de un agujero queda adentro del contorno exterior de la letra, así que tiene madre (`Parent != -1`). Si hay algún contorno con madre, hay un agujero.

- Sale de `PDI_U3_Segmentacion.py`, secciones "Contornos por jerarquía" y "Contornos que no tienen madres/padres". Ahí se filtran los contornos con `hierarchy[0][ii][3]==-1`, y nosotros contamos los que no cumplen eso.

Las dos reglas juntas quedan así: columna izquierda incompleta, A (u otro caracter) y se descarta. Columna llena con agujero, R. Columna llena sin agujero, L.

Antes de escribir la regla medimos todas las celdas de Condición Final con un solo caracter en las cuatro planillas (56 en total). En todas las L y R la primera columna mide exactamente el alto de la letra (12 px, o 10 en la planilla 4), y en todas las A mide entre 1 y 3 px. Los agujeros dan 0 en todas las L y 1 en todas las A y R. No hubo ningún caso dudoso.

### 3. Armar la imagen de salida

Creamos una imagen en blanco con `np.full` del tamaño justo para apilar los recortes uno debajo del otro, con un margen a la izquierda para el indicador. Después pegamos cada recorte de Nombre y Apellido en su lugar asignando la región por índices.

- Pegar un recorte en una imagen por índices está en `U2/Código-20260826/PI_U2_ej_blurred_face.py` (`img3[xi:xi+H, yi:yi+W] = sub_face`), y `np.full` para crear una matriz está en ese mismo archivo, en la versión con máscaras.
- El recorte sale de la imagen en grises, así que lo pasamos a 3 canales con `cv2.cvtColor` para poder dibujar en color, como hace `PDI_U3_Segmentacion.py` con `COLOR_GRAY2RGB` antes de dibujar contornos.

El indicador es doble: la letra de la condición escrita a la izquierda y un recuadro alrededor del nombre, en rojo para R y en azul para L.

- `cv2.rectangle` está en `PDI_U3_Segmentacion.py` (bounding boxes de las componentes conectadas) y en `PI_U2_ej_blurred_face.py`.
- `cv2.putText` está en `U2/Código-20260826/PI_U2_ej_video_face_detection_and_blur.py`.
- Los colores van en BGR porque la imagen se guarda con `cv2.imwrite`. `PI_U2_ej_blurred_face.py` muestra que OpenCV trabaja en BGR, y `cv2.imwrite` se usa en `U1/PDI_U1_Fundamentos_p1.py`.

Si en una planilla no queda ningún alumno L o R, igual se genera la imagen con el texto "Sin alumnos L/R", para que siempre haya una única salida por planilla.

## Verificación

Corrimos el script en las cuatro planillas y revisamos cada imagen contra la planilla original:

| Planilla | Registros con todo OK y L o R | Resultado |
|---|---|---|
| 1 | 10 | L: Bianca Monte, Farias Jorge, Juana Gomez, Amanda Santos, Nahuel Fausto, Julio Foglia. R: Rivas Hugo, Jorge Delgado, Jose Santini, Camila Godoy |
| 2 | 3 | L: Bianca Monte, Farias Jorge, Amanda Santos |
| 3 | 0 | Imagen con "Sin alumnos L/R" (ningún registro tiene los seis campos bien) |
| 4 | 4 | L: Nicolas Vega, Miguel Sastre. R: Jorge Delsio, Camila Godoy |

En la planilla 4 también hay registros con todo OK y condición A (Juana Gomez, Renzo Garcia), y quedan afuera, como corresponde. Los registros que tienen algún campo MAL no aparecen aunque su condición sea L o R, por ejemplo Nahuel Fausto en la planilla 2 (tiene "LL").

## Cosas que decidimos nosotros

- El criterio de la columna izquierda llena no está en el material. Sí están las herramientas (suma por columnas y bounding box), pero la idea de usarlas para separar A de L y R es nuestra y la validamos con las 56 celdas que hay en las planillas. Si apareciera otra letra con trazo vertical a la izquierda (B, D, P...), se clasificaría como L o R según tenga agujero o no. Como el enunciado solo habla de L y R, no lo cubrimos.
- El formato de la imagen (apilado vertical, letra más recuadro, rojo y azul) lo elegimos nosotros. El enunciado solo pide "algún indicador".
- La imagen se guarda al lado de la planilla de entrada. El enunciado no dice dónde.

## Próximos pasos (puntos c y d)

Esto es solo el enfoque. Todavía no está implementado.

### Punto c: archivo CSV

1. Usar la lista de OK/MAL por registro que ya devuelve `validar_planilla`.
2. Escribir una fila por registro: primero el ID (el número de registro, en el orden de la planilla) y después Legajo, Nombre y Apellido, Parcial 1, Parcial 2, Parcial 3 y Condición Final, cada uno con OK o MAL.
3. En el material de la cátedra no hay ningún ejemplo de cómo escribir un CSV. Lo más simple es el módulo `csv` de la biblioteca estándar de Python, y lo aclaramos porque no sale de la carpeta.

### Punto d: aplicar todo a las cuatro planillas

1. Recorrer los archivos `grade_sheet_<id>.png` con un `for` (dejando afuera `grade_sheet_empty.png`) y llamar para cada uno a la validación, a la imagen del punto b y al CSV del punto c. Cada salida lleva el id en el nombre, como ya pasa con `no_aprobados_grade_sheet_<id>.png`. Es parecido a cómo `U1/PDI_U1_p1_Letras.py` guarda un archivo por letra en la MEJORA 2.
2. Informar los resultados de cada planilla: cuántos registros quedaron completamente bien, qué campos fallaron más y qué alumnos quedaron en L o R.

## Fuentes usadas

| Archivo | Qué se tomó |
|---|---|
| `TUIA_PDI_TP1_2026_C2.pdf` (en el repo del grupo) | Consigna del punto b y suma por columnas de la AYUDA |
| `U3/Código-20260923/PDI_U3_Segmentacion.py` | `connectedComponentsWithStats` y `stats` (bounding box), `findContours` con `RETR_TREE` y jerarquía `[Next, Previous, First_Child, Parent]`, filtrado por `Parent`, `cv2.rectangle`, `cvtColor` de gris a color |
| `U2/Ejercicios-20260923/PDI_U2_p2_stain.py` | `np.sum` por columnas sobre una matriz booleana, uso de `pathlib.Path` |
| `U2/Código-20260826/PI_U2_ej_blurred_face.py` | Pegar un recorte en una imagen por índices, `np.full`, `cv2.rectangle`, orden BGR de OpenCV |
| `U2/Código-20260826/PI_U2_ej_video_face_detection_and_blur.py` | `cv2.putText` |
| `U1/PDI_U1_Fundamentos_p1.py` | `cv2.imwrite` |
| `U1/PDI_U1_p1_Letras.py` | Para el punto d: guardar un archivo por elemento con un `for` |
