
# Nivel 1
Objetivos:
   - Desarrollar un microservicio en flask que implemente la llamada [GET] /active con una respuesta dummy fija
   - Crear una imagen docker que contenga dicho microservicio y publicarla en dockerhub

   

Procedimiento realizado para crear el API/Micro servicio

Para completar esta parte se desarrolló el API(micro servicio) que responde una respuesta fija, en este caso el API está preparado para recibir dos parámetros(country y city) por medio de la URL en el endpoint /active
La estructura de carpetas y archivos para nuestra aplicación Flask es la siguiente:
```html
└── Nica-Venta
    ├── app
    │   ├── app.py
    │   ├── dummy_res.py
    │   └── requirements.txt
    └── Dockerfile
```
En el endpoint /active la aplicación responde con un json de acuerdo a la especificación del servicio:
```
{
   "active": True,
   "country": "ni",
   "city": "Leon",
 }

```
En este caso el endpoint /active está preparado para recibir dos parámetros de tipo GET(por medio de la URL) pero la respuesta NO proviene de la base de datos, sino que solamente muestra con cierto formato los datos que han sido enviados como parámetros, esto es porque en la aplicación flask se reciben los argumentos de esta manera:
```

@app.route('/activedummy_ventas = [{
   "active": True,
   "country": "ni",
   "city": "Leon",
 }
]
@app.route('/active')
def get_dummy():
   return jsonify(dummy_res.dummy_ventas)
```

Procedimiento realizado para la creación y publicación de la imagen de Docker

    URL de dockerhub: (https://cloud.docker.com/repository/docker/lissettedocker/nicaventas)

Para crear una imagen de docker que pueda correr el código de nuestro Micro servicio realizado con Flask se utilizó una imagen oficial de Docker para Python:

   URL de imagen de Python (https://hub.docker.com/_/python)
   
Esta imagen contiene lo necesario para correr código de Python, por lo cual a partir de ella se ha creado la imagen que contiene el código del Micro servicio, para reproducir una imagen igual a la que se ha creado debemos escribir el siguiente código en nuestro archivo Dockerfile:
    
```sh
FROM python
COPY app /app
RUN pip install -r /app/requirements.txt
WORKDIR app
CMD ["python", "app.py"]
EXPOSE 5000
```
 - Para construir y etiquetar la imagen ejecutamos esta línea en terminal:
 ```
docker build -t lissettedocker/nicaventas .
```
 - Para subir nuestra imagen recién creada ejecutamos la siguiente linea en terminal:
```sh
docker login
docker push 
```
 - Para correr un contenedor basado en nuestra imagen podemos ejecutar esta linea en terminal:
```sh
docker run -d -p 8000:8000 lissettedocker/nicaventas:N1
```
- Las Pruebas realizarlas con
```sh
curl localhost:8000/active?city=leon&country=ni. 
```
- La respuesta debe ser una respuesta JSON válida conforme a la especificación del servicio.

**Mi DockerHub**

https://cloud.docker.com/repository/docker/lissettedocker/nicaventas
