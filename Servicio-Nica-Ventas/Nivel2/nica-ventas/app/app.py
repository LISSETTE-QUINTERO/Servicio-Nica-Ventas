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
    vCountry = request.args.get('country')
    vCity = request.args.get('city');
    wl = Worklog(mysql, app.logger)
    js = wl.find_location(vCountry, vCity)
    if js is None:
        return jsonify('Registro no encontrado')
    else:
        return jsonify({'city':js[2], 'country':js[1], 'active':bool(js[3])})

@app.route('/active', methods=['POST'])
def post_active():
    try:
       payload = request.get_json()
       wl = Worklog(mysql, app.logger)
       wl.save_location(**payload)
       return jsonify({'payload': payload})
    except:
       return jsonify('Error, Verifique URL.')
@app.route('/active', methods=['PUT'])
def put_active():
#   try:
        payload = request.get_json()
        auth = request.headers.get("authorization", None)
        if not auth:
           return jsonify('Token no enviado')
        elif auth != "Bearer 2234hj234h2kkjjh42kjj2b20asd6918":
           return jsonify('El token no autorizado')
        else:
           wl = Worklog(mysql, app.logger)
           wl.state_location(**payload)
           return jsonify({'payload': payload, 'auth':auth})
#   except:
#        return jsonify('Error, Verifique URL.')
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
