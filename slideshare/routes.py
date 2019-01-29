from flask_restful import Resource
from slideshare import api
from slideshare.db import db_engine, db_metadata
from collections import defaultdict

from slideshare.resources.home import Home
from slideshare.resources.user import User, User_id

api.add_resource(Home, '/')
api.add_resource(User, '/user')
api.add_resource(User_id, '/user/<string:id>')

