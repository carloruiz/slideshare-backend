from flask_restful import Resource
from slideshare import api
from slideshare.db import db_engine, db_metadata
from collections import defaultdict

from slideshare.resources.home import Home
from slideshare.resources.user import User, User_id, User_institution
from slideshare.resources.slide import Slide, Slide_id, Slide_tag, Slide_user, Slide_institution, Upload
from slideshare.resources.tag import Tag
from slideshare.resources.institution import Institution
from slideshare.login import Login, Logout

api.add_resource(Upload, '/upload')

api.add_resource(Home, '/')
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')

api.add_resource(User, '/user')
api.add_resource(User_id, '/user/<string:id>')
api.add_resource(User_institution, '/user/institution/<string:id>')

api.add_resource(Slide, '/slide')
api.add_resource(Slide_id, '/slide/<string:id>')
api.add_resource(Slide_user, '/slide/user/<string:id>')
api.add_resource(Slide_tag, '/slide/tag/<string:id>')
api.add_resource(Slide_institution, '/slide/institution/<string:id>')

api.add_resource(Tag, '/tag')
api.add_resource(Institution, '/institution')

