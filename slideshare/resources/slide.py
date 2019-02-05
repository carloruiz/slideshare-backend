from flask import request
from flask_restful import Resource
from slideshare.db import (
    db_engine, 
    db_metadata, 
    Slide as Slide_Table,
    Slide_Tag as Slide_Tag_Table,
    Tag as Tag_Table,
    User as User_Table, 
    User_Meta as User_Meta_Table,
    Affiliation as Affiliation_Table,
    Institution as Institution_Table,
)
from slideshare.utils.db import execute_query, get_or_create
from sqlalchemy.sql import select
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

def SlideSchema(p):
   pass 

def tags_to_dict(row):
    res = []
    for affiliation in row['tags'].split('|'):
        id, tag = affiliation.split(',')
        res.append({'id': id, 'tag': tag})
    row['tags'] = res
    return row   

class Slide(Resource):
    def post(self):
        pass 

class Slide_id(Resource):
    def get(self, id):
        query = '''
            SELECT s.*, STRING_AGG(CONCAT(t.id, ',', t.tag), '|') as tags FROM slide as s 
            INNER JOIN slide_tag as st ON s.id = st.slide
            INNER JOIN tag as t ON t.id = st.tag
            WHERE s.id = %s
            GROUP BY s.id; 
            '''
        resp, code = execute_query(db_engine, query, params=(id,), 
            unique=True, transform=tags_to_dict)
        return resp, code

    def put(self, id):
        pass

class Slide_tag(Resource):
    def get(self, id):
        query = '''
            SELECT s.*, STRING_AGG(CONCAT(t.id, ',', t.tag), '|') FROM slide as s 
            INNER JOIN slide_tag as st ON s.id = st.slide
            INNER JOIN tag as t ON t.id = st.tag
            WHERE s.id IN (
                SELECT st.slide FROM slide_tag as st
                WHERE st.tag = %s
            ) GROUP BY s.id;
            '''

        resp, code = execute_query(db_engine, query, params=(id,), transform=tags_to_dict)
        return resp, code

class Slide_user(Resource):
    def get(self, id):
        query = '''
            SELECT s.*, STRING_AGG(CONCAT(t.id, ',', t.tag), '|') as tags FROM slide as s 
            INNER JOIN slide_tag as st ON s.id = st.slide
            INNER JOIN tag as t ON t.id = st.tag
            WHERE s.username = %s
            GROUP BY s.id;
            '''
        resp, code = execute_query(db_engine, query, params=(id,), transform=tags_to_dict)
        return resp, code


class Slide_institution(Resource):
    def get(self, id):
        query = ''' 
            SELECT s.*, STRING_AGG(CONCAT(t.id, ',', t.tag), '|') as tags FROM slide as s
            INNER JOIN slide_tag as st ON s.id = st.slide
            INNER JOIN tag as t ON t.id = st.tag
            WHERE s.id IN (
                SELECT u.id FROM "user" as u
                INNER JOIN affiliation as a ON a.user = u.id
                WHERE a.institution = %s
            ) GROUP BY s.id; 
            '''
        resp, code = execute_query(db_engine, query, params=(id,), transform=tags_to_dict)
        return resp, code

