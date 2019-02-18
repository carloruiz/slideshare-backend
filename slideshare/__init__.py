#from .app import app

from flask import Flask, request
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)


@app.before_request
def log_request():
    print(request.get_json())


@app.after_request
def add_cors_heaer(response):
    print(response)
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response


if __name__ == '__main__':
    app.run(debug=True)

from . import routes
from . import db
