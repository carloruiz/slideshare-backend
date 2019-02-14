from flask import request
from flask_restful import Resource
from slideshare.db import (
    db_engine, 
    db_metadata, 
    Slide_id as Slide_Id_Table,
    Slide as Slide_Table,
    Slide_Tag as Slide_Tag_Table,
    Tag as Tag_Table,
)
from slideshare.utils.db import execute_query, get_or_create
from slideshare.utils.processing import run_subprocess
from slideshare.utils.aws import aws_s3_uri, aws_s3_url

from sqlalchemy.sql import select
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from werkzeug.utils import secure_filename

from datetime import datetime, timezone
from threading import Thread
import sys
import tempfile
import os


class Upload(Resource):
    def post(self):
        print(request.get_json())
        print(request.files)
        print(request.form)
        print(request.form['size'])
        return {}, 200, {"Access-Control-Allow-Origin": '*'}

def tags_to_dict(row):
    res = []
    for affiliation in row['tags'].split('|'):
        id, tag = affiliation.split(',')
        res.append({'id': id, 'tag': tag})
    row['tags'] = res
    return row   


def strfmt_bytes(size):
    # MacOS displays different file size in teriminal vs finder
    # I chose to display finder size.. To get 'real' size use 
    # power = 1024
    power = 1000
    n = 0
    Dic_powerN = {0 : '', 1: 'K', 2: 'M', 3: 'G'}
    while size > power:
        size /=  power
        n += 1
    return str(round(size)) + ' ' + Dic_powerN[n]+'B'


def SlideSchema(p, resourceid):
    try:
        resp, err =  {
            "username": p['username'],
            "userid": p['userid'],
            "title": p['title'],
            "description": p['description'],
            "created_on": datetime.now(timezone.utc),
            "last_mod": datetime.now(timezone.utc),
            "url": aws_s3_url(os.environ['S3_PPT_BUCKET'], p['userid'], resourceid),
            "thumbnail": aws_s3_url(os.environ['S3_THUMB_BUCKET'], p['userid'], resourceid),
            "size": strfmt_bytes(p['size']),
        }, 0
    except KeyError as e:
        resp, err = "'%s' key is required" % e.args[0], 1

    return resp, err


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
        print('In post handler')
        # TOTEST exceptions inside thread
        # TODO tags
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
                aws_thumb_uri = aws_s3_uri(os.environ['S3_THUMB_BUCKET'], userid, resourceid)
                args = 'aws s3 cp --recursive --quiet {} {}'.\
                    format(thumb_dir, aws_thumb_uri)
                aws_flag = run_subprocess(args.split(), userid, timeout=20)

        def thread_two():
            try:
                s3.upload_file(tmp_dir+'/'+filename, 
                    os.environ['S3_PPT_BUCKET'], '{}/{}/'.format(userid, resourceid))
            except Exception as e:
               aws_flag = 1 
               raise e
                
        try:
            tmp_path = tempfile.TemporaryDirectory()
            s3 = boto3.resource('s3')
            aws_ppt_uri, aws_thumb_uri = None, None
            flag, aws_flag = 0, 0
            print('var initialization')
            
            # generate resource id
            conn = db_engine.connect()
            trans = conn.begin() 
            resourceid = conn.execute(Slide_Id_Table.insert()).inserted_primary_key[0]
            print('got resource id {}'.format(resourceid))

            # parse request form
            username, userid = request.form['username'], request.form['userid']
            print("username:%s, userid:%s" % (username, userid))

            # get file, extract filename, file extension
            f = request.files['file']
            filename = secure_filename(f.filename)
            idx = filename.rfind('.')
            name, ext = filename[:idx], filename[idx:]
            print("filename: %s, ext: %s" % (filename, ext))

            # create tmp directory and thumbnail directory
            thumb_dir = tmp_path+'/thumbs/'
            os.mkdir(thumb_dir)
            f.save(tmp_path+'/'+filename)
            print("saved file to tmp folder")

            threads = []
            for func in [thread_one, thread_two]:
                thread = Thread(target=func)
                thread.start()

            for thread in threads:
                thread.join()
           
            if flag or aws_flag:
                raise Exception
            
            # insert sql row to slide table
            new_slide_meta = SlideSchema(request.form, resourceid)
            res = conn.execute(Slide_Table.insert(), **new_slide_meta) 
            # tags (code identical to affiliations in user.py)
            
            tmp_path.close()
            trans.commmit()
            return {}, 204, {"Access-Control-Allow-Origin": '*'}
        except:
            tmp_path.close()
            trans.rollback()
            if aws_flag:
                args = 'aws s3 rm --recursive --quiet %s && ' % aws_thumb_uri + \
                       'aws s3 rm --quiet %s' % aws_ppt_uri
                aws_flag = run_subprocess(args.split(), userid, timeout=20)
            #log error
            return {}, 500, {"Access-Control-Allow-Origin": '*'}

    
    
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
            WHERE s.userid = %s
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

