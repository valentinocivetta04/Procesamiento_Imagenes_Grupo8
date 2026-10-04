# TP1: ecualización local de histograma y validación de planillas

Materia: Procesamiento de Imágenes I (IA 4.4), Tecnicatura Universitaria en Inteligencia Artificial, FCEIA, Universidad Nacional de Rosario. Año 2026, 2° semestre. Grupo 8.

## Autores

- Civetta, Valentino
- Frank, Maximiliano
- Fucci, Milagros
- Winter, Federico

## Descripción

El trabajo tiene dos problemas. La consigna completa está en `TUIA_PDI_TP1_2026_C2.pdf`.

El Problema 1 implementa la ecualización local de histograma (puntos a, b y c). Aplicamos la función a `Imagen_con_detalles_escondidos.tif` para encontrar los detalles ocultos de cada zona y comparamos el resultado con distintos tamaños de ventana, cuadradas y rectangulares.

El Problema 2 valida de forma automática planillas de calificaciones en formato imagen (puntos a, b, c y d). Para cada registro informa qué campos cumplen las reglas, genera una imagen con los alumnos que no aprobaron y guarda un CSV con los resultados. El script procesa en ciclo las cuatro planillas `grade_sheet_<id>.png`.

## Estructura del repositorio

```
.
├── README.md                                   Este archivo.
├── Informe_TP1_PDI_Grupo8.pdf                  Informe del trabajo práctico.
├── TUIA_PDI_TP1_2026_C2.pdf                    Consigna del TP.
├── requirements.txt                            Dependencias del proyecto.
├── .gitignore                                  Excluye .venv/, archivos temporales y los archivos de salida (no_aprobados_*.png y validacion_*.csv).
├── problema1.py                                Problema 1: ecualización local, detalles ocultos y análisis de ventanas.
├── problema2.py                                Problema 2: validación de planillas, imagen de no aprobados y CSV.
├── Imagen_con_detalles_escondidos.tif          Entrada del Problema 1 (256x256, 8 bits).
├── grade_sheet_empty.png                       Planilla vacía de ejemplo (no la procesa el script).
├── grade_sheet_1.png                           Entrada del Problema 2: planilla 1.
├── grade_sheet_2.png                           Entrada del Problema 2: planilla 2.
├── grade_sheet_3.png                           Entrada del Problema 2: planilla 3.
└── grade_sheet_4.png                           Entrada del Problema 2: planilla 4.
```

`problema2.py` genera al ejecutarse `no_aprobados_grade_sheet_<id>.png` (punto 2b) y `validacion_grade_sheet_<id>.csv` (punto 2c) junto a cada planilla. Esos archivos de salida no están en el repositorio.

## Requisitos

Python 3.13.16. Es la versión con la que ejecutamos y verificamos todos los comandos de este README.

| Librería | Versión | Uso |
|---|---|---|
| numpy | 2.5.3 | Arrays, sumas por filas y columnas |
| opencv-python | 5.0.0.93 | Bordes, ecualización, componentes conectadas, contornos |
| matplotlib | 3.11.2 | Figuras del Problema 1 |

`pip` instala junto con matplotlib estas dependencias: contourpy 1.4.0, cycler 0.12.1, fonttools 4.66.1, kiwisolver 1.5.1, packaging 26.3, pillow 12.3.0, pyparsing 3.3.3, python-dateutil 2.9.0.post0 y six 1.17.0.

El archivo `requirements.txt` no fija versiones. Con él, `pip` instala las versiones más recientes disponibles, que en nuestra ejecución fueron las de la tabla.

## Instalación

Desde la carpeta del repositorio, en Linux o macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Para instalar exactamente las versiones de la tabla:

```bash
pip install numpy==2.5.3 opencv-python==5.0.0.93 matplotlib==3.11.2
```

## Ejecución

Ejecutá los scripts desde la carpeta del repositorio, con el entorno virtual activado.

### problema1.py

```bash
python problema1.py
```

- Entrada: `Imagen_con_detalles_escondidos.tif`.
- Salida por consola: la lista de detalles ocultos del punto 1b, una línea por zona.
- Salida gráfica: cuatro ventanas de matplotlib (global contra local, detalles por zona, ventanas cuadradas y ventanas rectangulares). El script no guarda archivos. Cuando cerrás las ventanas termina.
- Sin pantalla (por ejemplo en un servidor), anteponé `MPLBACKEND=Agg`. En ese caso no se abre ninguna ventana y el script solo imprime la lista de detalles:

```bash
MPLBACKEND=Agg python problema1.py
```

El punto 1c calcula varias ventanas grandes píxel a píxel. La ejecución completa tardó unos 4 segundos en la máquina donde la medimos.

### problema2.py

```bash
python problema2.py
```

- Entrada: `grade_sheet_1.png`, `grade_sheet_2.png`, `grade_sheet_3.png` y `grade_sheet_4.png`, que el script busca al lado de `problema2.py`.
- Salida por consola, para cada planilla: el estado OK o MAL de cada campo de cada registro, el nombre de los archivos generados y un resumen (registros correctos, campos MAL por columna y cantidad de alumnos en R y en L).
- Archivos que genera, junto a cada planilla: `no_aprobados_grade_sheet_<id>.png` (punto 2b) y `validacion_grade_sheet_<id>.csv` (punto 2c). Si ya existen, los reescribe.

## Informe

El informe con la descripción de los ejercicios, el análisis de los problemas, las técnicas, el desarrollo paso a paso y las conclusiones está en [Informe_TP1_PDI_Grupo8.pdf](Informe_TP1_PDI_Grupo8.pdf).
