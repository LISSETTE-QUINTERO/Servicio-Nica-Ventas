from flask import Flask, jsonify, request, escape
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
            weather = requests.get('http://api.openweathermap.org/data/2.5/weather?q=' + payload['city'] + ',' + payload['country'] + '&appid=3225ae99d4c4cb46be4a2be004226918').json()      
       
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
            return jsonify({'cache':'miss', 'country': js[0], 'city': js[1], 'sku': js[2], 'min': str(js[3]), 'max': str(js[4]), 'var': str(js[5]), 'price':str(js[7]), 'description': js[6]})
    #except:
    #   return jsonify('Error, Verifique URL.')
#....................
#cache Miss hit

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
