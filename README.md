# Nivel 4

Objetivos:

 - Evolucionar la arquitectura existente para incluir un micro servicio que proporcione el API `[POST] /quote`, según lo especificado en el enunciado en Servicio de consulta de condiciones de venta
 - Añadir al archivo docker-compose el nuevo microservicio
 - Añadir políticas de cacheo de forma que si se solicita `[POST] /quote` con los mismos parámetros se responda desde la cache de `REDIS` en lugar de volver a realizar la consultas a OpenWeather y la BBDD. La valided de uno de estos datos cacheados será de 5 min. Con objeto de verificar que la cache funciona, incluir en la respuesta un campo cache como se hizo anteriormente.

## Desarrollo

La aplicación de NicaVentas cuenta con dos micro servicios con una estructura bastante simple, los cuales fueron creados para interactuar con el servicio de base de datos`(mysql`) y el servicio de caché(`redis`), el primero de estos dos servicios es el servicio de consulta de disponibilidad de ventas por país y ciudades, el segundo es el servicio de consulta de condiciones de venta, en este segundo servicio se hace uso del API de OpenWeatherMaps para consultar el estado del clima en el Pais y ciudad solicitado, esto con el fin de poder hacer una venta diferenciada de acuerdo al clima que se esté presentado en ese momento en la ciudad.
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
## Servicio de consulta de disponibilidad de ventas

Servicio web se emplea para consultar si se está autorizada la venta de productos en general en una ciudad concreta de un país haciendo uso del endpoint `[GET] /active?city=Leon&country=ni`.

El resultado de la invocación de este endpoint, a modo de ejemplo, será el siguiente:
```py
{
  "active": true,
  "country": "ni",
  "city": "Leon"
}
```
El campo active indica si la venta está autorizada (`true`) o no (`false`) en la correspondiente ciudad (`city`) del país (`country`) especificado en la llamada.

Una serie de operadores son los encargados de activar y desactivar las posibilidades de venta en las ciudades. Estos operadores disponen del siguiente endpoint del API para activar o desactivar la venta:

Modificar el estado de actividad de una ciudad de un país: URL: /active Method: PUT Auth required: YES Body format: Content-type: application/json Body payload:

```sh
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
# Servicio de consulta de condiciones de venta

El servicio de condiciones de venta permite consultar qué porcentaje de descuento se hará a un producto determinado. Los productos se identifican mediante un código único denominado `SKU`. A modo de ejemplo vamos a considerar dos productos:


| SKU | DESCRIPCION| PRECIO|
| ------ | ------ |------ |
| AZ00001  | Paraguas de señora estampado |10€|
| AZ00002 | Helado de sabor fresa |1€|

 	
El precio final de venta dependerá de dos factores: la ciudad y país de venta, y la condiciones meteorológicas de esa ciudad. La idea general es vender más caros los paraguas y más baratos los helados si estuviera lloviendo, y al contrario, abaratar los paraguas y encarecer helados si hiciera sol. Se proporcionará para esta consulta el endpoint `[GET] /price/<:sku>`.

Por ejemplo, si la venta se hace en León (Nicaragua) y está lloviendo en ese momento, la llamada `[POST] /quote` con `body`:
```sh
{
  "sku": "AZ00001",
  "country": "ni",
  "city": "Leon"
}
```
Respondería, por ejemplo:
```sh
{
  "sku": "AZ00001",
  "description": "Paraguas de señora estampado",
  "country": "ni",
  "city": "Leon",
  "base_price": 10,
  "variation": 1.5
}
```
El precio de los paraguas bajo estas condiciones sería de `10 x 1.5 = 15€`.

Para calcular la respuesta adecuada, el endpoint `[POST] /quote` dispondrá del API de un tercero, concretamente de `OpenWeather`, para consultar el tiempo meteorológico de una ciudad concreta de un país.

Con la información devuelta por el API de OpenWeather estamos en condiciones de comparar con las reglas de variación que hayamos creado en la base de datos:

| id_regla | ciudad| pais|SKU|min_condition|max_condition| variation|
| ------ | ------ |------ |------ |------ |------ |------ |
| 1   | Leon  |NI|AZ00001|500|599|1.5|
| 2  | Leon |NI|AZ00002|500|599|0.5|
 	 	 	 	
Supongamos que preguntamos al servicio meteorológico sobre las condiciones en Leon, Nicaragua, y obtenemos id=503 (very heavy rain). Consultamos a continuación a la base de datos y si se cumple al menos una regla de las que tengamos guardadas entonces el valor de variation será la variación que debemos usar. Si por el contrario no se cumpliera ninguna regla se podría considerar que la variación es 1, o lo que es lo mismo, que no hay variación.

# Procedimiento  para  crear y publicar las imágenes de Docker

- Crear una imagen de Docker que pueda correr el código de nuestros Micro servicios realizados con Flask se utilizó una imagen oficial de Docker para `Python`:

    URL de imagen de Python

Esta imagen contiene lo necesario para correr código de Python, por lo cual a partir de ella se ha creado la imagen que contiene el código del Micro servicio, para reproducir una imagen igual a la que se ha creado debemos escribir el siguiente código en nuestro archivo:

# Dockerfile
El DockerFile nos permitirá definir las funciones basicas del contenedor
```sh
FROM python  **La directiva FROM indica la imagen base de la cual partiremos
COPY /app /app 
RUN pip install -r /app/requirements.txt **Instalar y Ejecuta los comandos en  requirements
WORKDIR app  **Establece el directorio para las directivas de CMD que se ejecutarán
CMD ["python", "app.py"] **Configura comandos por defecto para ser ejecutado, o se pasa al punto de entrada ENTRYPOINT
EXPOSE 5000 **Expone un puerto al exterior
```

- Construir las imágenes de Docker y etiquetarlas ejecutamos:
```
docker build -t lissettedocker/nicaventas:N4C .
docker build -t lissettedocker/nicaventas:N4D .
```
- Para  empujar las imagenes creadas del servicio creadas ejecutamos:
```
docker login 
docker push lissettedocker/nicaventas:N4C
docker push lissettedocker/nicaventas:N4D
```
Al ejecutar las lineas de arriba se nos va a solicitar nuestras credenciales de dockerhub.

- Para ejecutar los servicios orquestados con docker-compose se requiere el archivo de entorno `environment` que contenga todas las credenciales y configuraciones de la aplicación:
```yml
environment:
                       - FLASK_DEBUG=1
                       - DATABASE_PASSWORD=nicaventaspass
                       - DATABASE_NAME=nicaventasdb
                       - DATABASE_USER=nicaventasuser
                       - DATABASE_HOST=nicaventas-db
                       - REDIS_LOCATION=redis
                       - REDIS_PORT=6379
```
También necesitamos el script de schema.sql para crear las tablas y rellenarla con datos para realizar pruebas:


# docker-compose

Para el funcionamiento de dos micro servicios, la base de datos y el servicio de cache con un solo comando, en este ejemplo se hace uso del orquestador docker compose, el cual utiliza un archivo yml para configurar y arrancar los servicios de la aplicación.

A continuación las lineas necesarias en el archivo docker-compose.yml
```yml
version: '3'
services:  
       redis:
              image: redis
              expose:
                       - 6379
       Disponibilidad:
               image: lissettedocker/nicaventas:N4D
               build:
                       context: ./Disponibilidad
                       dockerfile: Dockerfile
               ports:
                       - "8000:5000"
               volumes:
                       - ./Disponibilidad/app:/app
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
       Condiciones:
               image: lissettedocker/nicaventas:N4C
               build:
                       context: ./Condiciones
                       dockerfile: Dockerfile
               ports:
                       - "8001:5000"
               volumes:
                       - ./Condiciones/app:/app
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
                      - ./Condiciones/schema.sql:/docker-entrypoint-initdb.d/schema.sql
    
```
Ejecutar el demonio docker-compose:
```
docker-compose up
```
Ejecutar el demonio docker-compose en segundo plano: 
```
docker-compose up -d
```

## Servicio de consulta de disponibilidad de venta

- Probar  con: `curl localhost:8000/active?city=Leon&country=ni`. 
Devuelve respuesta JSON como esto:

```sh
{
  "active": false,
  "cache": "hit",
  "city": "Leon",
  "country": "ni"
}
curl localhost:8000/active?city=leon
```

- Guardar un nuevo registro en la base de datos podemos ejecutar esta linea en la terminal:
```
curl -d '{"city":"Leon", "country":"NI", "estado":"True"}' -H "Content-Type: application/json" -X POST localhost:8000/active
```
Debe responder un json con los datos del registro que han sido guardado:
```
{
  "active": true,
  "city": "Leon",
  "country": "ni"
}
```
- Comprobar que realmente se ha guardado en la base de datos podemos usar esta linea en la terminal:
```sh
curl localhost:8000/active?city=Leon&country=ni
```
La petición anterior nos devolverá el registro con los datos solicitados:

```sh
{
  "active": true,
  "cache": "miss",
  "city": "Leon",
  "country": "ni"
}
curl -d '{"city":"Leon", "country":"NI", "active":"1"}' -H "Content-Type: application/json" -X POST localhost:8000/active

       curl localhost:8000/active?city=Leon
```
La respuesta incluye un atributo llamado `"cache": "miss"` lo cual nos indica que la petición realizada ha llegado hasta la base de datos, pero si volvemos a hacer la misma petición veremos que ahora se nos devuelve el siguiente json con el atributo `"cache": "hit"` indicando que ahora los datos provienen de la cache, optimizando los tiempos de carga:

```sh
{
  "active": true,
  "cache": "hit",
  "city": "Leon",
  "country": "ni"
}
 curl localhost:8000/active?city=Leon
```
- Actualizar un registro podemos ejecutar la siguiente linea en terminal:
```sh
curl -d '{"city":"Leon", "country":"NI", "estado":"False"}' -H "Content-Type: application/json" -H "Authorization: Bearer 2234hj234h2kkjjh42kjj2b20asd6918" -X PUT localhost:8000/active
```
Para lograr esta petición con éxito es necesario que en los datos enviados se mande  el token de autorización, de lo contrario la petición devolverá un error, Si la petición se ejecuta sin problemas nos devuelve un json con el registro actualizado:
```sh
{
  "active": false,
  "city": "Leon",
  "country": "ni"
}
```

Para seguridad de actualización en la base de datos podemos usar esta linea en la terminal:
```sh
curl localhost:8000/active?city=Leon\&country=NI
```
debe retornar el registro actualizado, ahora veremos que también la cache ha sido borrada y se hizo la consulta en base de datos, tal como se nos indica con `"cache": "miss"`:

```sh
{
  "active": false,
  "cache": "miss",
  "city": "Leon",
  "country": "ni"
}
  curl localhost:8000/active?city=Leon
  ```

# Servicio de consulta de condiciones de venta

Este servicio  hace uso del API de OpenWeather para consultar el estado del clima de la ciudad donde se quiere realizar la venta, primeramente para este servicio tenemos disponible una ruta para consultar directamente el precio base de un producto del inventario:
```sh
curl 'localhost:8001/price/AZ00001'
curl 'localhost:8001/price/AZ00002'
```
Con los datos de pruebas que hemos insertado en la base de datos se tiene disponibles 2 artículos para consultar por medio de su SKU, el AZ00001 y el AZ00002.

- Al ejecutar la petición anterior  debe devolver un json similar a esto:
```sh
{
  "description": "Paraguas de señora estampado",
  "idSku": "AZ00001"
  "price": 10
}
```
 Al ejecutar la petición anterior  debe devolver un json similar a esto:
```sh
"description": "Helado de sabor fresa", 
  "idSku": "AZ00002", 
  "price": 10.0
}

```
- Para consultar la variación de precio de acuerdo al estado del clima en la ciudad donde se quiere realizar la venta podemos usar esta linea en la terminal:
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
Esto  indica que deberíamos vender los paraguas más baratos, pero si hacemos la misma petición para los Helados con la siguiente linea:
```sh
curl -X POST -d '{"city":"Leon","country":"ni","sku":"AZ00002"}' -H "Content-Type: application/json" http://127.0.0.1:8001/quote
```
el producto solicitado para el país y ciudad debe venderse más caro, de acuerdo al clima de ese momento:
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
## Construcción de los micro servicios

Los servicios para el API se crearon usando `Python` y `Flask` y algunas librerías de `Python` como `requests`, `redis`, a continuación el código fuente de Python para cada uno de los micro servicios

# Servicio de consulta de disponibilidad

schema.py
```sql
CREATE TABLE IF NOT EXISTS location (
       country varchar(2) NOT NULL,
       city varchar(100) NOT NULL,
       active bool NOT NULL,
       PRIMARY KEY (country, city)
) ENGINE=innodb;
CREATE TABLE IF NOT EXISTS products (
       sku varchar (7) NOT NULL,
       description varchar(30) NOT NULL,
       price float(5) NOT NULL,
       PRIMARY KEY (sku)
) ENGINE=innodb;
CREATE TABLE IF NOT EXISTS rules (
       id INT NOT NULL AUTO_INCREMENT,
       country varchar(2) NOT NULL,
       city varchar(100) NOT NULL,
       sku varchar (7) NOT NULL,
       min_condition int(3) NOT NULL,
       max_condition int(3) NOT NULL,
       variation DECIMAL(2,1) NOT NULL,
       PRIMARY KEY (id), index (country), index(city),
       FOREIGN KEY (sku) REFERENCES products (sku),
       foreign key (country,city) REFERENCES location (country,city)
) ENGINE=innodb;
INSERT INTO products (sku, description, price) VALUES('AZ00001','Paraguas de señora estampado', 10.0);
INSERT INTO products (sku, description, price) VALUES('AZ00002','Helado de sabor fresa', 10.0);
INSERT INTO location (country, city, active) VALUES('NI','Managua', false);
INSERT INTO location (country, city, active) VALUES('NI','Nueva Guinea', false);
INSERT INTO rules (country, city, sku, min_condition, max_condition, variation) values ('NI', 'Managua', 'AZ0000
1', 500,599, 1.5);
INSERT INTO rules (country, city, sku, min_condition, max_condition, variation) values ('NI', 'Managua', 'AZ0000
2', 500, 599, 0.5); 
INSERT INTO rules (country, city, sku, min_condition, max_condition, variation) values ('NI', 'Managua', 'AZ0000
1', 800, 804, 0.5); 
INSERT INTO rules (country, city, sku, min_condition, max_condition, variation) values ('NI', 'Managua', 'AZ0000
2', 800, 804, 1.5);
INSERT INTO rules (country, city, sku, min_condition, max_condition, variation) values ('NI', 'Nueva Guinea', 'A
Z00001', 500,599, 1.5);
INSERT INTO rules (country, city, sku, min_condition, max_condition, variation) values ('NI', 'Nueva Guinea', 'A
Z00002', 500, 599, 0.5); 
INSERT INTO rules (country, city, sku, min_condition, max_condition, variation) values ('NI', 'Nueva Guinea', 'A
Z00001', 800, 804, 0.5); 
INSERT INTO rules (country, city, sku, min_condition, max_condition, variation) values ('NI', 'Nueva Guinea', 'A
Z00002', 800, 804, 1.5); 
```
app.py 
```py
import os
from flask_mysqldb import MySQL
from worklog import Worklog
import redis
import requests 
import json
import sys

app = Flask(__name__)

app.config['MYSQL_HOST'] = os.environ['DATABASE_HOST']
app.config['MYSQL_USER'] = os.environ['DATABASE_USER']
app.config['MYSQL_PASSWORD'] = os.environ['DATABASE_PASSWORD']
app.config['MYSQL_DB'] = os.environ['DATABASE_NAME']
app.config['JSON_AS_ASCII'] = False;
mysql = MySQL(app)
redis_cli = redis.Redis(host=os.environ['REDIS_LOCATION'], port=os.environ['REDIS_PORT'])
#GET/price--------------------------
@app.route('/price/<idSku>')
def consultar(idSku):
    try:
       wl = Worklog(mysql, app.logger)
       js = wl.find_price(escape(idSku))
       
       response={
                    "price": float(js[2]),
                    "idSku": escape(idSku),
                    "description": js[1],
                }
       return jsonify(response)
    except:
      return jsonify({"message":"Datos no asociados"})
  #..................P0ST----------------
  @app.route('/quote', methods=['POST'])
def post_quote():
    #try:
       payload = request.get_json()
       key = payload['country'].lower() + '-' + payload['city'].lower() + '-' + payload['sku'].lower()        
       
       cache = redis_cli.get(key)       
       if cache:
           js = json.loads(cache)            
           
           response = {
                            "sku": js['sku'],
                            "country": js['country'],
                            "city": js['city'],
                            #"price": js['price'],
                            #"var": js['var'],
                            "cache": "hit"
                      }
           return jsonify(response)
       else:
            weather = requests.get('http://api.openweathermap.org/data/2.5/weather?q=' + payload['city'] + ',' +
 payload['country'] + '&appid=3225ae99d4c4cb46be4a2be004226918').json()      
       
            wl = Worklog(mysql, app.logger)
            js = wl.find_rules(weather['weather'][0]['id'], **payload)
            redis_cli.setex(key, 300, '{"country":"' + js[0] +
                                      '","city":"' + js[1] +
                                      '","sku":"' + js[2] +
                                      '","min":"' + str(js[3]) +
                                      '","max":"' +str(js[4])+
                                      '","var":"' +str(js[5])+
                                      '","description":"' +js[6]+
                                      '","price":'+str(js[7])+
                                      '}')
            return jsonify({'cache':'miss', 'country': js[0], 'city': js[1], 'sku': js[2], 'min': str(js[3]), 'm
ax': str(js[4]), 'var': str(js[5]), 'price':str(js[7]), 'description': js[6]})
    #except:
    #   return jsonify('Error, Verifique URL.')
#....................
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
```
requiriments.txt
```sh
Click==7.0
Flask==1.1.1
Flask-MySQL==1.4.0
Flask-MySQLdb==0.2.0
itsdangerous==1.1.0
Jinja2==2.10.1
MarkupSafe==1.1.1
mysqlclient==1.4.2.post1
PyMySQL==0.9.3
redis==3.2.1
Werkzeug==0.15.5
redis==3.2.1
worklog
requests
```
worklog.py
```sh
class Worklog:
   def __init__(self, dbcon, logger):
       self._dbcon=dbcon
       self._logger=logger
   def find_price(self, sku):
       sql = """
       select * from products  where sku="{}";
       """.format(  
             sku)
       cur = self._dbcon.connection.cursor()
       cur.execute(sql)
       rv = cur.fetchone()
       cur.close()
       return rv
   def find_rules(self, weather, **payload):
       sql = """
       select country
              , city
              , rl.sku
              , min_condition
              , max_condition
              , variation
              , pr.description
              , pr.price
       from rules as rl
       inner join products as pr on rl.sku = pr.sku
       where country = "{}" and city =  "{}" and  min_condition <= "{}" and max_condition >= "{}" and  rl.sku = 
"{}"; 
       """.format(  
              payload['country'],
              payload['city'],
              weather,
              weather,
              payload['sku'])
       cur = self._dbcon.connection.cursor()
       cur.execute(sql)
       rv = cur.fetchone()
       cur.close()
       self._logger.info(sql)
       self._logger.info(rv)
       return rv
```
