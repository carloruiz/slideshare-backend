from flask import request
from flask_restful import Resource
import json

class Institution(Resource):
    def get(self):
        with open('../data/institutions.json') as f:
            data = f.read()
        return json.dumps(data)
