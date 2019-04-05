from flask import request
from flask_restful import Resource
from slideshare import app
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
import boto3

from datetime import datetime, timezone
from threading import Thread, Event as ThreadEvent
import subprocess as sp
import json
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
            "id": resourceid,
            "username": p['username'],
            "userid": p['userid'],
            "title": p['title'],
            "description": p['description'],
            "created_on": datetime.now(timezone.utc),
            "last_mod": datetime.now(timezone.utc),
            "url": aws_s3_url(app.config['S3_PPT_BUCKET'], resourceid, ext='.pptx'),
            "thumbnail": aws_s3_url(app.config['S3_THUMB_BUCKET'], resourceid, ext='/'),
            "size": strfmt_bytes(int(p['size'])),
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
        # TOTEST exceptions inside thread
        # TODO tags
        def thread_one():
            args = 'libreoffice --headless --convert-to pdf %s --outdir %s' % \
                (tmp_path+filename,  tmp_path)

            flag = run_subprocess(args.split(), userid, timeout=60,
                exception=sp.TimeoutExpired)

            if flag: 
                print("Error occured with libreoffice conversion")
                err_flag.set()
                return
           
            try:
                s3.upload_file(tmp_path+name+'.pdf', 
                    app.config['S3_PDF_BUCKET'], 
                    '{}/{}.pdf'.format(resourceid, new_slide_meta['title'].replace(' ', '+')),
                    ExtraArgs={'ACL': 'public-read'}
                )
            except Exception:
                aws_flag.set()
            
            if aws_flag.is_set():
                print("Error uploading pdf to AWS")
                err_flag.set()
                return

            
            args = "pdftoppm -jpeg %s %s" % (tmp_path+name+'.pdf', thumb_dir) 
            flag = run_subprocess(args.split(), userid)
           
            if flag:
                print("Error occured in pdf to image conversion")
                err_flag.set()
                return
            
            for f in os.listdir(thumb_dir):
                os.rename(thumb_dir+'/'+f, thumb_dir+'/'+'0'*(7-len(f[1:]))+f[1:])
            
            
            args = 'aws s3 cp --recursive --quiet --acl public-read {} {}'.\
                format(thumb_dir, aws_s3_uri(app.config['S3_THUMB_BUCKET'], 
                    resourceid, ext='/'))
            flag = run_subprocess(args.split(), userid, timeout=30)
            aws_flag.set()

            if flag: 
                print("Error with aws image upload")
                err_flag.set()


        def thread_two():
            try:
                s3.upload_file(tmp_path+filename, 
                    app.config['S3_PPT_BUCKET'], 
                    '{}/{}.pptx'.format(resourceid, new_slide_meta['title'].replace(' ', '+')),
                    ExtraArgs={'ACL': 'public-read'}
                )
                aws_flag.set()
            except Exception as e:
                print("Error with aws pptx upload")
                err_flag.set()
                raise e
            print("done with thread 2")
        
        # TODO upload all tags in one call
        def thread_three():
            try:
                TT = Tag_Table
                slide_tags = []
                for tag_obj in tag_list:
                    print(tag_obj)
                    tag = {"tag": tag_obj['tag'].lower()}
                    tag_pk = get_or_create(conn, tag, TT, (TT.c.tag == tag['tag']))
                    slide_tags.append({"slide": resourceid, "tag": tag_pk})
                
                conn.execute(Slide_Tag_Table.insert(), slide_tags)
            except Exception as e:
                print("Error in slide_tag creation")
                print(e)
                err_flag.set()
            print("done with thread 3")
    
        try:
            tmp_dir = tempfile.TemporaryDirectory()
            tmp_path = tmp_dir.name +'/'
            s3 = boto3.client('s3')
            aws_ppt_uri, aws_thumb_uri = None, None
            tag_list = json.loads(request.form['tags'])
            err_flag, aws_flag = ThreadEvent(), ThreadEvent()
            
            # generate resource id
            conn = db_engine.connect()
            trans = conn.begin() 
            resourceid = conn.execute(Slide_Id_Table.insert()).inserted_primary_key[0]

            # parse request form
            new_slide_meta, err = SlideSchema(request.form, resourceid)
            if err:
                raise Exception(new_slide_meta)
            username, userid = new_slide_meta['username'], new_slide_meta['userid']

            # get file, extract filename, file extension
            f = request.files['file']
            filename = secure_filename(f.filename)
            idx = filename.rfind('.')
            name, ext = filename[:idx], filename[idx:]

            # create tmp directory and thumbnail directory
            thumb_dir = tmp_path+'thumbs/'
            os.mkdir(thumb_dir)
            f.save(tmp_path+filename)

            threads = []
            for func in [thread_one, thread_two, thread_three]:
                thread = Thread(target=func)
                threads.append(thread)
                thread.start()

            for thread in threads:
                thread.join()
           
            if err_flag.is_set():
                raise Exception
           
            print("Getting to sql")
            # insert sql row to slide table
            res = conn.execute(Slide_Table.insert(), **new_slide_meta) 
            print("did meta")
            # tags (code identical to affiliations in user.py)
            tmp_dir.cleanup()
            trans.commit()
            return {}, 200, {"Access-Control-Allow-Origin": '*'}
        except Exception as e:
            tmp_dir.cleanup()
            trans.rollback()
            if aws_flag.is_set():
                print('cleaning up aws')
                args = 'aws s3 rm --recursive --quiet %s' % \
                    aws_s3_uri(app.config['S3_THUMB_BUCKET'], resourceid, ext='/')
                run_subprocess(args.split(), userid, timeout=20)
                s3.delete_object(
                        Bucket=app.config['S3_PPT_BUCKET'], 
                        Key='{}/{}.pptx'.format(userid, resourceid))
            #log error
            if type(e) == IntegrityError:
                print('duplicate title error')
                return {
                        "field": "title", 
                        "error": "You already have a presentation with the same name"
                    }, 400
            print('raising some server exception')
            raise e
            
    
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

