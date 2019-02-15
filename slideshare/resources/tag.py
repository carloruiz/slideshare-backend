from flask import request
from flask_restful import Resource
from slideshare.db import db_engine, Tag as Tag_Table
class Tag(Resource):
    def get(self):
       return [dict(r) for r in db_engine.execute(Tag_Table.select())] 
        
