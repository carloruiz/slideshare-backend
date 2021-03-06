from sqlalchemy import Table, create_engine, MetaData
import os
from slideshare import app

db_engine = create_engine(app.config['DB_URI'])
db_metadata = MetaData(bind=db_engine)

User        = Table('user', db_metadata, autoload=True)
User_Meta   = Table('user_meta', db_metadata, autoload=True)
Affiliation = Table('affiliation', db_metadata, autoload=True)
Institution = Table('institution', db_metadata, autoload=True)
Slide_id    = Table('slide_id', db_metadata, autoload=True)
Slide       = Table('slide', db_metadata, autoload=True)
Tag         = Table('tag', db_metadata, autoload=True)
Slide_Tag   = Table('slide_tag', db_metadata, autoload=True)

