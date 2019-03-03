from flask import request, make_response
from flask import after_this_request
from flask_restful import Resource
from sqlalchemy.sql import select
import json

from slideshare.db import db_engine, User 
from slideshare.utils.auth import verify_password, generate_auth_token

class Login(Resource):
    def post(self):
        username, password = request.form['username'], request.form['password']
        query = select([User]).where(User.c.username == username)
        user = db_engine.execute(query).first()

        if not user or not verify_password(user, password):
            return {}, 400 

        token = generate_auth_token(user.id).decode('ascii')
        resp = make_response()
        # TODO add secure=True after adding ssl cert
        resp.set_cookie("auth_token", token, httponly=True, path=None)
        resp.set_cookie("userid", str(user.id), path=None)
        resp.set_cookie("username", user.username, path=None)
        return resp


class Logout(Resource):
    def get(self):
        resp = make_response()
        resp.set_cookie("auth_token", "rubbish", max_age=0)
        resp.set_cookie("userid", "morerubbish", max_age=0)
        resp.set_cookie("username", "evenmore", max_age=0)
        return resp
