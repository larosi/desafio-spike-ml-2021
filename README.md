# desafio-spike-ml-2021

## Generar Docker 📦
Abrir la linea de comandos en el directorio del proyecto y hacer Build del Dockerfile con tag *spike-milk:v1*
```bash
docker build . -t spike-milk:v1
```

El comando para ejecutar la imagen de docker tiene la siguiente estructura, es necesario compartir el volumen de la ruta actual y también el puerto 8889 para poder exponer la API 
```bash
docker run --rm -it \
	-v ${PWD}:/workspace \
	-p 8889:8889 \
	spike-milk:v1 \
	<comando a ejectuar>
```

## Ejecutar Pipeline ⚙️

Para el pipeline de limpieza de datos y entrenamiento de modelo se utilizó [DVC](https://dvc.org/) el cual es una libería opensource para control de versiones de datos, modelos de ML y pipelines (es un git pensado para datos!), los pasos, parámetros y dependencias del Pipeline y estan definidos en el archivo *dvc.yaml*, para ejecutarlo solo hay que usar el comando *dvc repro*

con docker:
```bash
docker run --rm -it -v ${PWD}:/workspace spike-milk:v1 dvc repro
```
sin docker es simplemente:
```bash
dvc repro
```
automáticamente verificára si los scripts y artefactos de cada stage del pipeline estan actualiazados, si no lo estan ejecuta los stages que sean necesarios para que lo estén

## Levantar API de predicción de precios 📋

Ejecutar el script *model_api.py* desde la imagen de docker, compartiendo el volumen de la ruta actual y el puerto 8889 para poder acceder a la API fuera del docker.

```bash
docker run --rm -it -v ${PWD}:/workspace -p 8889:8889 spike-milk:v1 python model_api.py
```
## Uso de la API
La API se implementó con Flask, debido a que no estaba definida la forma en que el usuario final hará la petición a la API se implementaron dos alternativas, se puede usar una u otra cambiando el endpoint al hacer el request, el script *post_request_sample.py* contiene un ejemplo que envía un Post request a la API implementada con datos aleatorios extraidos de los .csv de datos historicos
```bash
python post_request_sample.py
```

la respuesta esta en formato JSON con el campo *precio_leche* con el valor predicho por el modelo:
```
{"precio_leche": "237.80880504382918"}
```
### Alternativa 1 fecha como Query:
El usuario envia un Post request a la ruta http://127.0.0.1:8889/predict_by_date indicando la fecha en el campo 'date' formato "dia-mes-año",
el programa buscará en los .csv los datos macroeconómicos y precipitaciones requeridos, posteriormente ejecutará el modelo de predicción de precios, la ventaja es que es más simple para el usuario pero está limitado por los datos disponibles en los .csv lo ideal sería que existiera algun otro servicio SQL que mantenga actualizado estos datos. 

```
{'date' : '01-03-2018'}
```
### Alternativa 2 request con datos:
El usuario envia un Post request a la ruta http://127.0.0.1:8889/predict_by_rows con los datos de tres meses consecutivos de los 46 datos macroeconómicos y de precipitaciones usados para entrenar el modelo en formato json, posteriormente el programa transforma estos datos en features para que luego el modelo pueda hacer la predicción de precios
```
'Coquimbo': {0: 2.54989542289229, 1: 2.29345097637011, 2: 0.0833333334392485},
 'Valparaiso': {0: 2.8417207621425, 1: 0.473230523178233, 2: 1.50115259712586},
 'Metropolitana_de_Santiago': {0: 6.00555370139246,
  1: 2.20317114333641,
  2: 3.83914430114447},

  ...

 'PIB_Servicios_empresariales': {0: 121944143, 1: 112452457, 2: 114769302},
 'PIB_Servicios_de_vivienda': {0: 947775692, 1: 926675063, 2: 925382127},
 'PIB_Servicios_personales': {0: 930780416, 1: 817476045, 2: 168024554},
 'PIB_Administracion_publica': {0: 574799242, 1: 573039158, 2: 575579649},
 'PIB_a_costo_de_factores': {0: 112395018, 1: 107541772, 2: 122452712},
 'PIB': {0: 122707677, 1: 117685853, 2: 13377956},
```

## Comentarios y posibles mejoras 📋
- En el notebook habian dos modelos, en el pipeline por defecto se dejó el segundo que usa solo las variables macroeconómicas y precipitaciones, ya que usar el precio de la leche de meses anteriores como input va en contra del enunciado del desafio
- En el Pipeline por simplicidad solo hay dos stages, limpieza-preparación y entrenamiento, sin embargo se podrían incluir o dividir en más como por ejemplo una etapa de creación de variables, extracción de métricas, generación de reportes, etc
- Noté que la etapa de limpieza elimina muchos registros que tienen datos NaN, se podría incluir una etapa previa de selección de variables considerando las columnas de support que entregó el gridsearch, quizás algunas de las columnas con NaN no son relevantes para el modelo y podrian eliminarse antes en lugar de quitar todas las filas que tengan NaN.

