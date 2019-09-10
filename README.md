# Servicio-Nica-Ventas
Nivel 4
Descripción general

La aplicación de NicaVentas cuenta con dos micro servicios con una estructura bastante simple, los cuales fueron creados para interactuar con el servicio de base de datos(postgres) y el servicio de caché(redis), el primero de estos dos servicios es el servicio de consulta de disponibilidad de ventas por país y ciudades, el segundo es el servicio de consulta de condiciones de venta, en este segundo servicio se hace uso del API de OpenWeatherMaps para consultar el estado del clima en el Pais y ciudad solicitado, esto con el fin de poder hacer una venta diferenciada de acuerdo al clima que se esté presentado en ese momento en la ciudad.
Estructura de carpetas y archivos para la aplicación NicaVentas:
```
├── Condiciones
│   ├── app
│   │   ├── app.py
│   │   ├── app.py.save
│   │   ├── __pycache__
│   │   │   ├── app.cpython-37.pyc
│   │   │   └── worklog.cpython-37.pyc
│   │   ├── requirements.txt
│   │   └── worklog.py
│   ├── Dockerfile
│   ├── schema.sql
│   └── schema.sql.save
├── Disponibilidad
│   ├── app
│   │   ├── app.py
│   │   ├── __pycache__
│   │   │   ├── app.cpython-37.pyc
│   │   │   ├── requirements.txt
│   │   │   └── worklog.cpython-37.pyc
│   │   ├── requirements.txt
│   │   └── worklog.py
│   └── Dockerfile
├── docker-compose.ym
└── docker-compose.yml
```
Servicio de consulta de disponibilidad de ventas

Servicio web se emplea para consultar si se está autorizada la venta de productos en general en una ciudad concreta de un país haciendo uso del endpoint [GET] /active?city=leon&country=ni.

El resultado de la invocación de este endpoint, a modo de ejemplo, será el siguiente:
```
{
  "active": true,
  "country": "ni",
  "city": "Leon"
}
```
El campo active indica si la venta está autorizada (true) o no (false) en la correspondiente ciudad (city) del país (country) especificado en la llamada.

Una serie de operadores son los encargados de activar y desactivar las posibilidades de venta en las ciudades. Estos operadores disponen del siguiente endpoint del API para activar o desactivar la venta:

Modificar el estado de actividad de una ciudad de un país: URL: /active Method: PUT Auth required: YES Body format: Content-type: application/json Body payload:
```
{
  "active": true,
  "country": "ni",
  "city": "Leon"
}
```
Esta llamada solo se atenderá si incluye en las cabeceras HTTP un token de autenticación como el siguiente:
```
Authorization: Bearer 2234hj234h2kkjjh42kjj2b20asd6918
```
Servicio de consulta de condiciones de venta

El servicio de condiciones de venta permite consultar qué porcentaje de descuento se hará a un producto determinado. Los productos se identifican mediante un código único denominado SKU. A modo de ejemplo vamos a considerar dos productos:
SKU 	DESCRIPCION 	PRECIO
AZ00001 	Paraguas de señora estampado 	10€
AZ00002 	Helado de sabor fresa 	1€

El precio final de venta dependerá de dos factores: la ciudad y país de venta, y la condiciones meteorológicas de esa ciudad. La idea general es vender más caros los paraguas y más baratos los helados si estuviera lloviendo, y al contrario, abaratar los paraguas y encarecer helados si hiciera sol. Se proporcionará para esta consulta el endpoint [GET] /price/<:sku>.

Por ejemplo, si la venta se hace en León (Nicaragua) y está lloviendo en ese momento, la llamada [POST] /quote con body:
```
{
  "sku": "AZ00001",
  "country": "ni",
  "city": "Leon"
}
```
Respondería, por ejemplo:
```
{
  "sku": "AZ00001",
  "description": "Paraguas de señora estampado",
  "country": "ni",
  "city": "Leon",
  "base_price": 10,
  "variation": 1.5
}
```
El precio de los paraguas bajo estas condiciones sería de 10 x 1.5 = 15€.

Para calcular la respuesta adecuada, el endpoint [POST] /quote dispondrá del API de un tercero, concretamente de OpenWeather, para consultar el tiempo meteorológico de una ciudad concreta de un país.

Con la información devuelta por el API de OpenWeather estamos en condiciones de comparar con las reglas de variación que hayamos creado en la base de datos:
id_regla 	ciudad 	pais 	SKU 	min_condition 	max_condition 	variation
1 	Leon 	NI 	AZ00001 	500 	599 	1.5
2 	Leon 	NI 	AZ00002 	500 	599 	0.5
						

Supongamos que preguntamos al servicio meteorológico sobre las condiciones en Leon, Nicaragua, y obtenemos id=503 (very heavy rain). Consultamos a continuación a la base de datos y si se cumple al menos una regla de las que tengamos guardadas entonces el valor de variation será la variación que debemos usar. Si por el contrario no se cumpliera ninguna regla se podría considerar que la variación es 1, o lo que es lo mismo, que no hay variación.
Procedimiento realizado para la creación y publicación de las imágenes de Docker

    - URL de dockerhub del servicio de consulta de Disponibilidad

    - URL de dockerhub del servicio de consulta de Condiciones de venta

Para crear una imagen de Docker que pueda correr el código de nuestros Micro servicios realizados con Flask se utilizó una imagen oficial de Docker para Python:

    URL de imagen de Python

Esta imagen contiene lo necesario para correr código de Python, por lo cual a partir de ella se ha creado la imagen que contiene el código del Micro servicio, para reproducir una imagen igual a la que se ha creado debemos escribir el siguiente código en nuestro archivo:
# Dockerfile
```sh
FROM python
LABEL maintainer "Darwin Salinas <salinash2000@gmail.com>"
RUN mkdir /app
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt
ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.2.1/wait /wait
RUN chmod +x /wait
CMD /wait && python app.py
```
Puedes reemplazar el nombre y correo del manteiner de la imagen

Para construir las imágenes de Docker y etiquetarlas ejecutamos esta línea en terminal dentro de la carpeta correspondiente de cada micro servicio:
```
docker build -t darwinsalinas/nicaventas-disponibilidad-nivel4 .
docker build -t darwinsalinas/nicaventas-condiciones-nivel4 .
```
Para subir nuestras imágenes recién creadas ejecutamos lo siguiente en terminal:
```
docker login && docker push darwinsalinas/nicaventas-condiciones-nivel4
docker login && docker push darwinsalinas/nicaventas-disponibilidad-nivel4
```
Al ejecutar las lineas de arriba se nos va a solicitar nuestras credenciales de dockerhub.

Para correr los servicios orquestados con docker-compose se requiere la presencia de un archivo de entorno .env que contenga todas las credenciales y configuraciones de la aplicación:
```
POSTGRES_DB=nicaventas
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_PORT=5432
DB_SERVICE=nicaventas-db
APP_SETTINGS=config.DevelopmentConfig
FLASK_DEBUG=1
TOKEN=2234hj234h2kkjjh42kjj2b20asd6918
REDIS_PORT=6379
REDIS_LOCATION=redis
API_KEY_OWM=3d3ea700fcb655178274e26b3af34ccd
```
Aparte del archivo de configuración anteriormente descrito, también necesitamos el script de initdb.sql para crear las tablas y rellenarla con datos para realizar pruebas:


 

# docker-compose

Para poner en funcionamiento los dos micro servicios, mas la base de datos y el servicio de cache con un solo comando, en este ejemplo se hace uso del orquestador Docker compose, compose utiliza un archivo YML para configurar y arrancar los servicios de la aplicación.

A continuación las lineas necesarias en el archivo docker-compose.yml
```
version: '3'
services:
  nicaventas-db:
    restart: always
    image: postgres
    container_name: "nicaventas-db"
    env_file:
      - .env
    ports:
      - "54320:5432"
    volumes:
      - ./initdb.sql:/docker-entrypoint-initdb.d/initdb.sql
    # volumes:
    #   - my_dbdata:/var/lib/postgresql/data

  nicaventas-disponibilidad:
    restart: always
    depends_on:
      - nicaventas-db
    environment:
      WAIT_HOSTS: nicaventas-db:5432
    container_name: "nicaventas-disponibilidad-us"
    image: darwinsalinas/nicaventas-disponibilidad-nivel4
    env_file:
    - .env
    ports:
      - 5000:5000
    command: flask run --host=0.0.0.0

  nicaventas-condiciones:
    restart: always
    depends_on:
      - nicaventas-db
    environment:
      WAIT_HOSTS: nicaventas-db:5432
    container_name: "nicaventas-condiciones-us"
    image: darwinsalinas/nicaventas-condiciones-nivel4
    env_file:
    - .env
    ports:
      - 5001:5000
    command: flask run --host=0.0.0.0

  redis:
    image: redis
    expose:
      - 6379

volumes:
  my_dbdata:
```
Ya con estos archivos podemos correr nuestros servicios con la siguiente instrucción:
```
docker-compose up
```
Si queremos poner a correr ls servicios en segundo plano podemos agregarle el flag -d:
```
docker-compose up -d
```

Servicio de consulta de disponibilidad de venta

Probar con Postman, el navegador o también lo puedes hacer con: curl localhost:5000/active?city=leon&country=ni. La respuesta que devuelve debe ser una respuesta JSON como esto:

```
{
  "active": false,
  "cache": "hit",
  "city": "leon",
  "country": "ni"
}
curl localhost:8000/active?city=leon
```

Para guardar un nuevo registro en la base de datos podemos ejecutar esta linea en la terminal:
```
curl -X POST -d '{"city":"ElRama","country":"ni","active":true}' -H "Content-Type: application/json" localhost:5000/active
```
Esto nos debe responder un json con los datos del registro que ha sido guardado:
```
{
  "active": true,
  "city": "ElRama",
  "country": "ni"
}
```
Si queremos comprobar que realmente se ha guardado en la base de datos podemos usar esta linea en la terminal:
```
curl localhost:5000/active?city=ElRama&country=ni
```
La petición anterior nos devolverá el registro con los datos solicitados:

```sh
{
  "active": true,
  "cache": "miss",
  "city": "ElRama",
  "country": "ni"
}
       curl localhost:5000/active?city=ElRama
```
Si nos fijamos con detenimiento, en este caso la respuesta incluye un atributo llamado "cache": "miss" lo cual nos indica que la petición realizada ha llegado hasta la base de datos, pero si volvemos a hacer la misma petición veremos que ahora se nos devuelve el siguiente json con el atributo "cache": "hit" indicando que ahora los datos provienen de la cache, optimizando los tiempos de carga:

```sh
{
  "active": true,
  "cache": "hit",
  "city": "ElRama",
  "country": "ni"
}
 curl localhost:5000/active?city=ElRama
```
Para actualizar un registro podemos ejecutar la siguiente linea en terminal:
```sh
curl -X PUT -d '{"city":"El Rama","country":"ni","active":false}' -H "Content-Type: application/json" -H "Authorization: Bearer 2234hj234h2kkjjh42kjj2b20asd6918" localhost:5000/active
```
Como se puede notar, para lograr esta petición con éxito es necesario que junto con los datos enviado se mande también el token de autorización, de lo contrario la petición devolverá un error, Si la petición se ejecuta sin problemas nos devuelve un json con el registro actualizado:
```sh
{
  "active": false,
  "city": "ElRama",
  "country": "ni"
}
```

Si queremos estar totalmente seguros de que se ha actualizado en la base de datos podemos usar esta linea en la terminal:
```sh
curl localhost:5000/active?city=ElRama&country=ni
```
Ademas de devolvernos el registro actualizado, ahora veremos que también la cache ha sido borrada y se hizo la consulta en base de datos, tal como se nos indica con "cache": "miss":

```sh
{
  "active": false,
  "cache": "miss",
  "city": "ElRama",
  "country": "ni"
}
  curl localhost:5000/active?city=ElRama
  ```

Servicio de consulta de condiciones de venta

Como se mencionó al principio, este servicio tiene la particularidad que hace uso del API de OpenWeather para consultar el estado del clima de la ciudad donde se quiere realizar la venta, primeramente para este servicio tenemos disponible una ruta para consultar directamente el precio base de un producto del inventario:
```sh
curl http://127.0.0.1:8001/price/AZ00001
```
Con los datos de pruebas que hemos insertado en la base de datos tenemos disponibles 2 artículos para consultar por medio de su SKU, el AZ00001 y el AZ00002.

Al ejecutar la petición anterior se nos debe devolver un json similar a esto:
```sh
{
  "description": "Paraguas de señora estampado",
  "price": 10
}
```
Para consultar la variación de precio de acuerdo al estado del clima en la ciudad donde se quiere realizar la venta podemos usar esta linea en la terminal:
```sh
curl -X POST -d '{"city":"Leon","country":"ni","sku":"AZ00001"}' -H "Content-Type: application/json" http://127.0.0.1:8001/quote
```
Si al momento de realizar la petición está lloviendo en la ciudad y país especificado entonces obtendremos una variación que nos permita vender mas caro los paraguas, al momento en el que se realizó la petición no estaba lloviendo en León por lo que el servicio me devuelve esta respuesta:
```sh
{
  "base_price": 10.0,
  "cache": "miss",
  "city": "Leon",
  "country": "ni",
  "description": "Paraguas de se\u00f1ora estampado",
  "sku": "AZ00001",
  "variation": 0.5
}
```
Esto nos indica que deberíamos vender los paraguas mas baratos, pero si hacemos la misma petición para los Helados con la siguiente linea:
```sh
curl -X POST -d '{"city":"Leon","country":"ni","sku":"AZ00002"}' -H "Content-Type: application/json" http://127.0.0.1:5001/quote
```
Ahora vemos que el producto solicitado para el país y ciudad debe venderse mas caro, de acuerdo al clima de ese momento:
```sh
{
  "base_price": 1.0,
  "cache": "miss",
  "city": "Leon",
  "country": "ni",
  "description": "Helado de sabor fresa",
  "sku": "AZ00002",
  "variation": 1.5
}
```
Construcción de los micro servicios

Los servicios para el API fueron creados usando Python y Flask y algunas librerías de Python como Flask-SQLAlchemy, requests, redis, a continuación el código fuente de Python para cada uno de los micro servicios
Servicio de consulta de disponibilidad
```sh
app.py
```
