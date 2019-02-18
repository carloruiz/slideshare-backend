from flask_restful import Resource
import json

class Institution(Resource):
    def get(self):
        with open('slideshare/data/institutions.json') as f:
            data = f.read()
        return json.loads(data)
