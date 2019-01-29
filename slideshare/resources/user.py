from flask import request
from flask_restful import Resource
from slideshare.db import (
    db_engine, 
    db_metadata, 
    User as User_Table, 
    User_Meta as User_Meta_Table,
    Affiliation as Affiliation_Table,
    Institution as Institution_Table
)
from slideshare.utils.db import get_or_create
from sqlalchemy.sql import select
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from marshmallow import Schema, fields
from datetime import datetime, timezone


def UserSchema(p):
    return {
        "username": p['username'],
        "email": p['email'],
        'password': p['password']
    }

def UserMetaSchema(p, new_pk):
    return {
        "userid": new_pk,
        "firstname":p['firstname'],
        "lastname": p['lastname'],
        "joined_on": datetime.now(timezone.utc),
        "last_login": datetime.now(timezone.utc),
        "user_type": p['user_type']
    }

def InstitutionSchema(institution_str):
    name, state = institution_str.split(',')
    return {
        'name': name,
        'state': state
    }

class User(Resource):
    def post(self):
        payload = request.get_json()
        new_user = UserSchema(payload)
        try:
            user_pk = db_engine.execute(User_Table.insert(), **new_user).inserted_primary_key[0]
        except IntegrityError as e:
            return {"message": "username or email is already taken"}, 400
        
        new_user_meta = UserMetaSchema(payload, user_pk)
        res = db_engine.execute(User_Meta_Table.insert(), **new_user_meta)

        IT = Institution_Table
        for affiliation in payload['affiliations']:
            inst = InstitutionSchema(affiliation)
            inst_pk = get_or_create(db_engine, inst, IT, 
                (IT.c.name == inst['name']) &
                (IT.c.state == inst['state']))
            db_engine.execute(Affiliation_Table.insert(), user=user_pk, institution=inst_pk)

        return {}

def UserUpdate(p):
    mutable_columns = ['username', 'email']
    return {k: v for k,v in p.items() if k in mutable_columns}

def UserMetaUpdate(p):
    mutable_columns = ['firstname', 'lastname', 'user_type']
    return {k: v for k,v in p.items() if k in  mutable_columns}

class User_id(Resource):
    def get(self, id):
        U, UM = User_Table.c, User_Meta_Table.c
        s = select([
            U.id, 
            U.username, 
            U.email, 
            UM.firstname, 
            UM.lastname, 
            UM.joined_on, 
            UM.last_login, 
            UM.user_type]).where(
                (U.id == UM.userid) & 
                (U.id == id)
            )
        user = db_engine.execute(s).first()
        return dict(user)

    def put(self, id):
        payload = request.get_json()
        user_update = UserUpdate(payload)
        user_meta_update = UserMetaUpdate(payload)
        try:
            if user_update:
                stmt = User_Table.update().\
                    where(User_Table.c.id == id).\
                    values(**user_update)
                db_engine.execute(stmt)
            if user_meta_update:
                stmt = User_Meta_Table.update().\
                    where(User_Meta_Table.c.userid == id).\
                    values(**user_meta_update)
                db_engine.execute(stmt)
        except IntegrityError as e:
            return {"message": "username or email already taken"}, 400

        return {}        


