from flask import Flask, request
from flask_restful import Resource, Api
from config import config
from .utils.gunicorn import make_aiohttp_app
import json

app = Flask(__name__)
app.config.update(config)
api = Api(app)
aioapp = make_aiohttp_app(app)

from . import routes
from . import db


@app.after_request
def add_cors_heaer(response):
    response.headers['Access-Control-Allow-Origin'] = config['ORIGIN']
    response.headers['Access-Control-Allow-Methods'] = 'POST, PUT, GET, OPTIONS'
    response.headers['Access-Control-Allow-Credentials'] = "true"
    return response


if __name__ == '__main__':
    print("running flask as main")
    app.run(debug=True)

