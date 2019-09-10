
# Nivel 2

Objetivos:

  - Ampliar el microservicio par que implemente la llamada [POST] /active. El estado, la ciudad y el país se deberá almacenar en una base de datos relacional.
  - Modificar el microservicio para que la llamada [GET] /active obtenga sus resultados desde la base de datos.
  - Orquestar el funcionamiento del microservicio con el de la base de datos haciendo uso de docker-compose. La base de datos en concreto es indiferente, pero se recomienda utilizar postgres, mysql o mariadb
   - Crear una imagen docker que contenga dicho microservicio y publicarla en dockerhub

## Desarollo

Esta aplicación fue creada con `python`, `mysql` y el micro framewok `Flask`,  se ha creado una imagen de Docker basada en la [imagen oficial de Python](https://hub.docker.com/_/python).

La estructura directorios y archivos de la aplicación es la siguiente:



### El archivo Dockerfile

- Para crear la imagen con el micro servicio se ha creado un archivo Dockerfile con el siguiente contenido:

```sh
FROM python *Imagen de Docker vamos a heredar o extender:
COPY app /app
RUN pip install -r /app/requirements.txt
WORKDIR app
CMD ["python", "app.py"]
EXPOSE 5000

```

Crear una carpeta dentro y poner los archivos de la aplicación Flask dentro del la imagen:

```
COPY app /app
WORKDIR  app
```

Instalar los requerimientos especificados en el archivo de requirements.txt:

```
RUN pip install -r /app/requirements.txt
```


La imagen se ejecuta con el comando que arranca la aplicación:

```
CMD ["python", "app.py"]

```

- Construir la imagen

Para construir la imagen se debe ejecutar el siguiente comando en la terminal, en la misma ruta donde se encuentra ubicado el archivo Dockerfile:
```
docker build -t lissettedocker/nicaventas:N2 .
```
En mi caso yo le he construido y etiquetado para poderla subir a [mi repositorio de Docker hub](https://cloud.docker.com/repository/docker/lissettedocker/nicaventas) posteriormente, para subir la imagen de recién construida se debe ejecutar el siguiente comando en la terminal:
```
docker login
docker push lissettedocker/nicaventas:N2
```
- Contruir  docker-compose

Para probar  el funcionamiento del micro servicio creado se ha creado una receta con docker-compose, el cual orquesta un servicio para la base de datos y el servicio para la aplicación Flask.

```sh 
version: '3'
services:
       nica-ventas:
               image: lissettedocker/nicaventas:N2
               build:
                       context: ./nica-ventas
                       dockerfile: Dockerfile
               ports:
                       - "8000:5000"
               volumes:
                       - ./nica-ventas/app:/app
               command: flask run --host=0.0.0.0
               environment:
                       - FLASK_DEBUG=1
                       - DATABASE_PASSWORD=nicaventaspass
                       - DATABASE_NAME=nicaventasdb
                       - DATABASE_USER=nicaventasuser
                       - DATABASE_HOST=nicaventas-db
                       - REDIS_LOCATION=redis
                       - REDIS_PORT=6379
               command: flask run --host=0.0.0.0
       nicaventas-db:
              image: mysql:5
              environment:
                      - MYSQL_ROOT_PASSWORD=123qwe
                      - MYSQL_DATABASE=nicaventasdb
                      - MYSQL_USER=nicaventasuser
                      - MYSQL_PASSWORD=nicaventaspass
              expose:
                     - 3306
              volumes:
                      - ./nica-ventas/schema.sql:/docker-entrypoint-initdb.d/schema.sql
      

```

En el archivo `docker-compose` se especifican los servicios que se deben arrancar y para el correcto funcionamiento de los mismos primeramente necesitamos crear un archivo `environment` con las configuraciones y credenciales de nuestra bade de datos:
```sh 
- FLASK_DEBUG=1
- DATABASE_PASSWORD=nicaventaspass
- DATABASE_NAME=nicaventasdb
- DATABASE_USER=nicaventasuser
- DATABASE_HOST=nicaventas-db
- REDIS_LOCATION=redis
- REDIS_PORT=6379
``` 
Este archivo de entorno (environment) será compartido con ambos servicios, en él tendremos el nombre de la base de datos a la cual debe conectarse nuestra aplicación Flask, en este caso la base de datos llamada `nica-ventas`.

Ademas del nombre de la base de datos también tenemos algunas configuraciones para el entorno de Flask, específicamente el modo de depuración está activado en esta configuración.

### Arrancar los contenedores orquestados con docker-compose:
```
docker-compose up &
```
## Funcionamiento del servicio de consulta de disponibilidad de ventas

Servicio web se emplea para consultar si se está autorizada la venta de productos en general en una ciudad concreta de un país. Para ello se construirá un API REST, y concretamente para esta consulta se implementará un endpoint `[GET] /active?city=leon&country=ni`.

El resultado de la invocación de este endpoint, a modo de ejemplo, será el siguiente:
```
{
  "active": true,
  "country": "ni",
  "city": "Leon"
}
```
El campo `active` indica si la venta está autorizada (`true`) o no (`false`) en la correspondiente ciudad (`city`) del país (`country`) especificado en la llamada.

Una serie de operadores son los encargados de activar y desactivar las posibilidades de venta en las ciudades. Estos operadores el siguiente endpoint del API para activar o desactivar la venta:

Modificar el estado de actividad de una ciudad de un país: **URL**: `/active` **Method**: `PUT` **Auth required**: YES **Body format**: `Content-type: application/json` **Body payload**:

```
{
  "active": true,
  "country": "ni",
  "city": "Leon"
}

```

Esta llamada solo se atenderá si incluye en las cabeceras HTTP un token de autenticación como el siguiente:

`Authorization: Bearer 2234hj234h2kkjjh42kjj2b20asd6918`

El token es un secreto compartido entre los encargados y el sistema. Para este ejemplo, el token `2234hj234h2kkjjh42kjj2b20asd6918` será siempre este.

[Mi DockerHub](https://cloud.docker.com/repository/docker/lissettedocker/nicaventas)

