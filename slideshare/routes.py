from flask_restful import Resource
from slideshare import api
from slideshare.db import db_engine, db_metadata
from collections import defaultdict

from slideshare.resources.home import Home
from slideshare.resources.user import User, User_username, User_institution
from slideshare.resources.slide import Slide, Slide_id, Slide_tag, Slide_user, Slide_institution
from slideshare.resources.slide import Upload



api.add_resource(Home, '/')
api.add_resource(User, '/user')
api.add_resource(User_username, '/user/<string:username>')
api.add_resource(User_institution, '/user/institution/<string:id>')

api.add_resource(Upload, '/upload')

api.add_resource(Slide, '/slide')
api.add_resource(Slide_id, '/slide/<string:id>')
api.add_resource(Slide_user, '/slide/user/<string:id>')
api.add_resource(Slide_tag, '/slide/tag/<string:id>')
api.add_resource(Slide_institution, '/slide/institution/<string:id>')

