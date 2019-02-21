#from .app import app

from flask import Flask, request
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)


@app.before_request
def log_request():
    print(request.form)


@app.after_request
def add_cors_heaer(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'POST, PUT, GET, OPTIONS'
    print(response.headers)
    return response


if __name__ == '__main__':
    app.run(debug=True)

from . import routes
from . import db
