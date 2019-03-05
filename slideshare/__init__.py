from flask import Flask, request
from flask_restful import Resource, Api
from config import config
import json

app = Flask(__name__)
app.config.update(config)
api = Api(app)

from . import routes
from . import db


@app.before_request
def log_request():
    print(json.dumps(request.__dict__, default=lambda o: '<not serializable>', indent=2))


@app.after_request
def add_cors_heaer(response):
    response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
    response.headers['Access-Control-Allow-Methods'] = 'POST, PUT, GET, OPTIONS'
    response.headers['Access-Control-Allow-Credentials'] = "true"
    print(response)
    return response

if __name__ == '__main__':
    app.run(debug=True)

