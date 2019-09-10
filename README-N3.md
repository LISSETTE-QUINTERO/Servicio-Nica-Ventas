

# Nivel 3

Esta aplicación fue creada con `python`, `postgres` y el micro framewok `Flask`, (entre otras librerías/dependencias) se ha creado una imagen de Docker basada en la [imagen oficial de Python](https://hub.docker.com/_/python).

La estructura directorios y archivos de la aplicación es la siguiente:

```
├── docker-compose.yml
└── nica-ventas
    ├── app
    │   ├── app.py
    │   ├── __pycache__
    │   │   ├── app.cpython-37.pyc
    │   │   ├── requirements.txt
    │   │   └── worklog.cpython-37.pyc
    │   ├── requirements.txt
    │   └── worklog.py
    ├── Dockerfile
    └── schema.sql


```
##  archivo Dockerfile

Para crear la imagen con el micro servicio se ha creado un archivo Dockerfile con el siguiente contenido:

```
FROM python
COPY app /app
RUN pip install -r /app/requirements.txt
WORKDIR app
CMD ["python", "app.py"]
EXPOSE 5000

```

A continuación un explicación corta de lo que hace el archivo Dockerfile:

En el archivo Dockerfile se especifica de que imagen de Docker vamos a heredar o extender:

```
FROM python

```

Crear una carpeta dentro y poner los archivos de la aplicación Flask dentro del la imagen:

```
COPY app /app
RUN pip install -r /app/requirements.txt
WORKDIR app

```

Instalar los requerimientos especificados en el archivo de requirements.txt:

```
RUN pip install -r /app/requirements.txt

```

Ya por ultimo se ejecuta el comando que arranca la aplicación:

```
CMD ["python", "app.py"]

```

- Construir la imagen

Para construir la imagen se debe ejecutar el siguiente comando en la terminal, en la misma ruta donde se encuentra ubicado el archivo Dockerfile:
```
 docker build -t lissettedocker/nicaventas:N3.
```
En mi caso yo le he construido y etiquetado para poderla subir a [mi repositorio de Docker Hub](https://cloud.docker.com/repository/docker/lissettedocker/nicaventas) posteriormente, para subir la imagen de recién construida se debe ejecutar el siguiente comando en la terminal:
```
docker login 
docker push lissettedocker/nicaventas:N3
```
- Contruir docker-compose

Para probar de forma fácil el funcionamiento del micro servicio creado se ha creado una receta con docker-compose, el cual orquesta un servicio para redis, uno para la base de datos y por ultimo el servicio para la aplicación Flask.

```sh
version: '3'
services:  
       redis:
              image: redis
              expose:
                       - 6378
       nica-ventas:
               image: lissettedocker/nicaventas:N3
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

Como se puede apreciar en el archivo `docker-compose` se especifican los servicios que se deben arrancar y para el correcto funcionamiento de los mismos primeramente necesitamos crear un archivo `environment` con las configuraciones y credenciales de nuestra bade de datos:
```sh
- FLASK_DEBUG=1
- DATABASE_PASSWORD=nicaventaspass
- DATABASE_NAME=nicaventasdb
- DATABASE_USER=nicaventasuser
- DATABASE_HOST=nicaventas-db
- REDIS_LOCATION=redis
- REDIS_PORT=6379
```

Este archivo de entorno (environment) será compartido con ambos servicios, en él tendremos el nombre de la base de datos a la cuál debe conectarse nuestra aplicación Flask, en este caso la base de datos llamada `nica-ventas`.

Ademas del nombre de la base de datos también tenemos algunas configuraciones para el entorno de Flask, específicamente el modo de depuración está activado en esta configuración y la configuración para redis.

### Arrancar los contenedores orquestados con docker-compose:
```
docker-compose up
```
Si quisiéramos arrancar los servicios en segundo plano podemos agregarle el flag '&'
```
docker-compose up &
```


## Funcionamiento del servicio de consulta de disponibilidad de ventas

Servicio web se emplea para consultar si se está autorizada la venta de productos en general en una ciudad concreta de un país. Para ello se construirá un API REST, y concretamente para esta consulta se implementará un endpoint `[GET] /active?city=Leon&country=ni`.

El resultado de la invocación de este endpoint, a modo de ejemplo, será el siguiente:

{
  "active": true,
  "country": "ni",
  "city": "Leon"
}

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

### Probar el Servicio de consulta de disponibilidad de venta

Probar con Postman, el navegador o también lo puedes hacer con: `curl localhost:8000/active?city=Leon\&country=NI`. La respuesta que devuelve debe ser una respuesta JSON como esto:
```
{
  "active": true, 
  "cache": "hit", 
  "city": "Leon", 
  "country": "NI"
}
```     

Para `guardar` un nuevo registro en la base de datos podemos ejecutar esta linea en la terminal:
``` 
curl -d '{"city":"Leon", "country":"NI", "estado":"True"}' -H "Content-Type: application/json" -X POST localhost:8000/active
``` 
Esto nos debe responder un json con los datos del registro que ha sido guardado:
``` 
{
  "mensaje": "Registro existente"
}
``` 
Si queremos comprobar que realmente se ha guardado en la base de datos podemos usar esta linea en la terminal:
``` 
curl localhost:8000/active?city=Leon\&country=NI 
``` 
La petición anterior nos devolverá el registro con los datos solicitados:
``` 
{
  "active": true, 
  "cache": "miss", 
  "city": "Leon", 
  "country": "NI"
}
   
curl localhost:8000/active?city=Leon
``` 
Si nos fijamos con detenimiento, en este caso la respuesta incluye un atributo llamado `"cache": "miss"` lo cual nos indica que la petición realizada ha llegado hasta la base de datos, pero si volvemos a hacer la misma petición veremos que ahora se nos devuelve el siguiente json con el atributo `"cache": "hit"` indicando que ahora los datos provienen de la cache, optimizando los tiempos de carga:
``` 
{
  "active": true, 
  "cache": "hit", 
  "city": "Leon", 
  "country": "NI"
}


``` 
Para `actualizar` un registro podemos ejecutar la siguiente linea en terminal:
``` 
curl -d '{"city":"Leon", "country":"NI", "estado":"False"}' -H "Content-Type: application/json" -H "Authorization: Bearer 2234hj234h2kkjjh42kjj2b20asd6918" -X PUT localhost:8000/active
``` 
Como se puede notar, para lograr esta petición con éxito es necesario que junto con los datos enviado se mande también el token de autorización, de lo contrario la petición devolverá un error, Si la petición se ejecuta sin problemas nos devuelve un json con el registro actualizado:
``` sh
{
  "active": false,
  "city": "Leon",
  "country": "ni"
}
``` 
Si queremos estar totalmente seguros de que se ha actualizado en la base de datos podemos usar esta linea en la terminal:

``` curl localhost:8000/active?city=Leon\&country=NI 
``` 


Ademas de devolvernos el registro actualizado, ahora veremos que también la caché ha sido borrada y se hizo la consulta en base de datos, tal como se nos indica con `"cache": "miss"`:

```sh

{
  "active": true, 
  "cache": "miss", 
  "city": "Leon", 
  "country": "NI"
}
curl localhost:8000/active?city=Leon

``` 
[Mi DockerHub](https://cloud.docker.com/repository/docker/lissettedocker/nicaventas)
