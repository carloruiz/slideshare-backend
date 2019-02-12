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
from slideshare.utils.processing import run_subprocess
from sqlalchemy.sql import select
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from werkzeug.utils import secure_filename

import pprint
import sys
import os


class Upload(Resource):
    def post(self):
        f = request.files['file']
        filename = secure_filename(f.filename)
        f.save('/Users/carloruiz/' + filename)
        
        '''
        body = request.get_json()
        with open(body['filename'], 'w') as f:
            f.write(body['file'])
        '''
        return {}, 200, {'Access-Control-Allow-Origin': '*'}

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
        '''
        *Thread1
        1. do conversion and img split
        2. upload thumbs to aws
        *Thread2
        1. upload pptx file to aws
        *After join
        generate sql row..
        '''
        # save incoming file locally

        
        f = request.files['file']
        filename = secure_filename(f.filename)
        idx = filename.rfind('.')
        name, ext = filename[:idx], filename[idx:]

        tmp_path = tempfile.TemporaryDirectory()
        thumb_dir = tmp_path+'/thumbs/'
        os.mkdir(thumb_dir)
        
        f.save(tmp_path+'/'+filename)

        def thread_one():
            args = 'libreoffice --headless --convert-to pdf %s --outdir %s' % \
                (tmp_path+'/'+filename,  tmp_path)
            flag = run_subprocess(args.split(), userid, 
                exception=sp.TimeoutExpired, timeout=20)
                
            if not flag:
                args = "pdftoppm -jpeg %s %s" % (tmp_dir+'/'+name+'.pdf', thumb_dir) 
                flag = run_subprocess(args.split(), userid, timeout=20)
           
            os.remove(tmp_path+'/'+name+'.pdf')
            for f in os.listdir(thumb_dir):
                os.rename(thumb_dir+'/'+f, thumb_dir+'/'+'0'*(7-len(f[1:]))+f[1:])
            
            
            if not flag:
                args = 'aws s3 cp --recursive --quiet {} s3://slide-share-thumbs/{}/{}/'.\
                    format(thumb_dir, userid, resourceid)
                flag = run_subprocess(args.split(), userid, timeout=20)

        def thread_two():
            args = 'aws s3 cp --quiet {} s3://slide-share/{}/{}/'.format(
                tmp_dir+'/'+filename, userid, resourceid)
            flag = run_subprocess(args.split(), userid, timeout=20)
        
                  

        tmp_path.close()

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

