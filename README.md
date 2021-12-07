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
automáticamente verificára si los scripts y artefactos de cada stage del pipeline estan actualiazados, si no estarlos ejecuta los stages que sean necesarios para que lo estén

## Levantar API de predicción de precios 📋

Ejecutar el script *model_api.py* desde la imagen de docker, compartiendo el volumen de la ruta actual y el puerto 8889 para poder acceder a la API fuera del docker.

```bash
docker run --rm -it -v ${PWD}:/workspace -p 8889:8889 spike-milk:v1 python model_api.py
```

La API se implementó en flask, para probarla esta un codigo de ejemplo *post_request_sample.py* que lee y envia una fila del .csv que se usó para entrenar el modelo, a través de un POST request a la ruta http://127.0.0.1:8889/model_api con un body con los datos de la fila en formato JSON.

```bash
python post_request_sample.py
```

la respuesta esta en formato JSON con el campo *precio_leche* con el valor predicho por el modelo:
```
{"precio_leche": "237.80880504382918"}
```

## Comentarios y posibles mejoras 📋
- En el notebook habian dos modelos, en el pipeline solo se incluyó el primero que usa las variables macroeconómicas y el precio de la leche de meses anteriores, pero podrian incluirse ambos y que la selección sea un parámetro de configuración en el *dvc.yaml*
- Si se implementan ambos modelos se podria incluir un paso de validación de los datos en la API, por ejemplo si el request incluye información de los precios de la leche entonces se utiliza el primer modelo (que tiene mejor desempeño), si no esta esa información entonces usar el segundo modelo
- En el Pipeline por simplicidad solo hay dos stages, limpieza-preparación y entrenamiento, sin embargo se podrían incluir o dividir en más como por ejemplo una etapa de creación de variables, extracción de métricas, generación de reportes, etc