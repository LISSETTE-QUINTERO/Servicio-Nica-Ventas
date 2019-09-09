from flask import Flask, jsonify, request, escape
import os
from flask_mysqldb import MySQL
from worklog import Worklog
import redis

app = Flask(__name__)

app.config['MYSQL_HOST'] = os.environ['DATABASE_HOST']
app.config['MYSQL_USER'] = os.environ['DATABASE_USER']
app.config['MYSQL_PASSWORD'] = os.environ['DATABASE_PASSWORD']
app.config['MYSQL_DB'] = os.environ['DATABASE_NAME']

mysql = MySQL(app)

redis_cli = redis.Redis(host=os.environ['REDIS_LOCATION'], port=os.environ['REDIS_PORT'])

@app.route('/active', methods=['GET'])
def get_active():
    #try:
        country = request.args.get('country')
        city = request.args.get('city');
        key = country.lower() + '_' + city.lower()
        state = redis_cli.get(key) 

        if state:
            response = {
                            "country":country,
                            "city":city,
                            "active":bool(state),
                            "cache":"hit"
                       }
        else:
             wl=Worklog(mysql,app.logger)
             js=wl.find_location(country,city)
             
             if js is None:
                 response = {"mensaje":"Registro no identificado"}
             else:
                 redis_cli.set(key,escape(js[2]))
                 response = {
                                "country":js[0],
                                "city":js[1],
                                "active":bool(js[2]),
                                "cache":"miss"
                            }
     
        return jsonify(response)
  #  except:
       # return jsonify({"mensaje":"Error Verifique URL"})
@app.route('/active', methods=['POST'])
def post_active():
    try:
       payload = request.get_json()
       wl = Worklog(mysql, app.logger)
       js=wl.find_location(payload['country'],payload['city'])
       if js is None:
           wl.save_location(**payload)
           response = {
               "mensaje":"Registro guardado",
               "country":payload['country'],
               "city":payload['city']
               } 
       else:
           response = {"mensaje":"Registro existente"}
       return jsonify(response)
    except:
        return jsonify({"mensaje": "error"})
@app.route('/active', methods=['PUT'])
def put_active():
    try:
        payload = request.get_json()
        auth = request.headers.get("authorization", None)
        if not auth:
           return jsonify('Token no enviado')
        elif auth != "Bearer 2234hj234h2kkjjh42kjj2b20asd6918":
           return jsonify('Token no autorizado')
        else:
           wl = Worklog(mysql, app.logger)
           wl.state_location(**payload)
          
           response= {
                           "mensaje": "Registro actualizado",
                           "token": auth,
                           "country": payload['country'],
                           "city": payload['city'],
                           "active": payload['active']
                      }       
        return jsonify(response)
    except:
        return jsonify({"mensaje": "error"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
