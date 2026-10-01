# TP1 PDI – Problema 2c y 2d: CSV de resultados y aplicación a las cuatro planillas

Procesamiento de Imágenes I (IA 4.4) · TUIA – FCEIA – UNR · 2026, 2° semestre

Con estos dos puntos queda terminado el Problema 2. Todo sigue en `problema2.py`:

```bash
python problema2.py    # procesa grade_sheet_1..4 (punto d)
```

Por cada planilla imprime la validación del punto a, guarda la imagen del punto b (`no_aprobados_grade_sheet_<id>.png`), guarda el CSV del punto c (`validacion_grade_sheet_<id>.csv`) y muestra un resumen.

## Qué piden los puntos c y d

Del enunciado (`TUIA_PDI_TP1_2026_C2.pdf`, Problema 2):

- c. Un archivo CSV con una fila por registro. La primera columna es un ID que respeta el orden de la planilla, y después va una columna por campo (Legajo, Nombre y Apellido, Parcial 1, Parcial 2, Parcial 3 y Condición Final) con OK o MAL.
- d. Aplicar el algoritmo en forma cíclica a las cuatro planillas `grade_sheet_<id>.png` e informar los resultados.

## Punto c: el CSV

No hubo que procesar nada nuevo de la imagen. `validar_planilla` ya devuelve, desde el punto b, la lista de OK/MAL de cada registro en el mismo orden que la planilla, así que el CSV es escribir esa lista en un archivo de texto:

- una primera línea con los nombres de las columnas, copiados tal cual del enunciado (c.ii);
- una línea por registro con su número (1 a 20) como ID y los seis resultados separados por comas.

Las filas vacías de la planilla también van al CSV, con todo MAL, porque el enunciado pide una fila por registro de la planilla y el ID tiene que coincidir con el orden.

Acá no hay nada del material de la cátedra: ningún archivo de la carpeta escribe archivos de texto ni CSV. Usamos lo más básico de Python (`open` y `write`), sin agregar librerías. Ya lo habíamos avisado en los documentos de 2a y 2b.

El nombre del archivo sale del de la planilla (`validacion_` + nombre sin extensión), igual que la imagen del punto b. Para eso usamos `pathlib.Path`, que aparece en `U2/Ejercicios-20260923/PDI_U2_p2_stain.py`.

## Punto d: las cuatro planillas en ciclo

El bloque principal del script recorre las planillas con un `for`. Para cada una:

1. Llama una sola vez a `validar_planilla` (punto a), que imprime OK/MAL por campo y devuelve la imagen, las líneas de la tabla y los resultados.
2. Le pasa esos datos a `imagen_no_aprobados` (punto b). Antes esta función llamaba a la validación por su cuenta. La cambiamos para que reciba los datos y así cada planilla se procesa una sola vez.
3. Guarda el CSV (punto c).
4. Imprime un resumen: cuántos registros tienen los seis campos bien, cuántos MAL hay en cada campo y cuántos alumnos quedaron en R y en L.

Los nombres de las planillas se arman con el índice (`grade_sheet_{k}.png` para k de 1 a 4). Es el mismo recurso que usa `U1/PDI_U1_p1_Letras.py` en la MEJORA 2 para nombrar un archivo por letra con un f-string. Armando los nombres así queda afuera `grade_sheet_empty.png`, que no tiene registros.

## Resultados

| Planilla | Registros correctos | MAL por campo (Leg / Nom / P1 / P2 / P3 / Cond) | No aprobados |
|---|---|---|---|
| 1 | 15 de 20 | 5 / 5 / 5 / 5 / 5 / 5 | 4 R, 6 L |
| 2 | 3 de 20 | 8 / 9 / 7 / 4 / 7 / 8 | 0 R, 3 L |
| 3 | 0 de 20 | 10 / 9 / 7 / 5 / 8 / 8 | ninguno |
| 4 | 6 de 20 | 6 / 7 / 4 / 5 / 5 / 6 | 2 R, 2 L |

Lo que se ve en los números:

- La planilla 1 es la "limpia". Los únicos MAL son las 5 filas vacías (3, 11, 14, 15 y 20), que fallan en todos los campos.
- La planilla 3 no tiene ningún registro completo. Casi todos los errores son de los mismos tipos que en la 2: legajos con dígitos de más o de menos o con espacios, nombres de una sola palabra o muy largos, notas vacías o de tres caracteres ("100", "AUS") y condiciones como "LL", "RR" o "Rec".
- En las cuatro planillas las filas vacías cuentan como registros con todo MAL (3 filas en la 2 y la 4, 3 en la 3 y 5 en la 1).

## Verificación

- El script corre sin errores con las cuatro planillas.
- La salida del punto a es idéntica a la de antes del cambio, en las cuatro planillas. Lo comparamos línea por línea.
- Cada CSV tiene 21 líneas (encabezado + 20 registros), 7 columnas, los IDs del 1 al 20 en orden y exactamente los mismos OK/MAL que imprime la consola. Esto también lo chequeamos automáticamente con las cuatro planillas.
- Las imágenes del punto b tienen los mismos alumnos, en el mismo orden y con la misma letra que antes de simplificar su formato (ver `Problema2b_explicacion.md`).

## Cosas que decidimos nosotros

- Escribir el CSV con `open`/`write`. El material no tiene ningún ejemplo, así que usamos lo más simple de Python base.
- El encabezado del CSV usa "Nombre y Apellido", como pide c.ii. En la consola sigue saliendo "Nombre y apellido", como en el ejemplo del punto a. El enunciado usa las dos formas.
- Los CSV y las imágenes se guardan al lado de cada planilla. El enunciado no dice dónde.

## Estado del TP

- [x] Problema 1: a, b y c
- [x] Problema 2: a, b, c y d

No quedan puntos del enunciado sin resolver. Antes de entregar convendría consultar con la cátedra si los 12 caracteres del nombre incluyen el espacio. Hoy no lo cuentan (ver `Problema2a_explicacion.md`), y si hubiera que contarlo cambiaría el resultado de nombres como AMANDA SANTOS o NAHUEL FAUSTO.

## Fuentes usadas

| Archivo | Qué se tomó |
|---|---|
| `TUIA_PDI_TP1_2026_C2.pdf` (en el repo del grupo) | Consigna de c (ID, orden y nombres de las columnas, valores OK/MAL) y de d |
| `U1/PDI_U1_p1_Letras.py` | Nombrar archivos de salida con el índice en un f-string, dentro de un `for` (MEJORA 2) |
| `U2/Ejercicios-20260923/PDI_U2_p2_stain.py` | `pathlib.Path` para armar rutas |
| Sin fuente en el material | Escritura del CSV con `open`/`write` (Python base) |
