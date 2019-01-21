from sqlalchemy import (
    Table, MetaData, Column, 
    Integer, String, ForeignKey, 
    DateTime, UniqueConstraint,
    PrimaryKeyConstraint, create_engine
)
from datetime import datetime, timezone
from config import DB

metadata = MetaData()

user = Table('user', metadata,
    Column('id', Integer, primary_key=True),
    Column('username', String(15), unique=True),
    Column('email', String, unique=True),
    Column('password', String),
    extend_existing=True,
)

user_meta = Table('user_meta', metadata,
    Column('id', Integer, primary_key=True),
    Column('userid', Integer, ForeignKey('user.id', ondelete="SET NULL"), unique=True), 
    Column('joined_on', DateTime, default=datetime.now(timezone.utc)),
    Column('last_login', DateTime, default=datetime.now(timezone.utc)),
    Column('user_type', String(15)),
    extend_existing=True,
)

slide = Table('slide', metadata,
    Column('id', Integer, primary_key=True),
    Column('title', String(30)),
    Column('url', String, unique=True),
    Column('user', Integer, ForeignKey('user.id', ondelete='CASCADE')),
    Column('size', String(20)),
    Column('description', String),
    Column('created_on', DateTime, default=datetime.now(timezone.utc)),
    Column('last_mod', DateTime, default=datetime.now(timezone.utc)),
    Column('thumbnail', String, unique=True),
    extend_existing=True
)

institution = Table('institution', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String),
    Column('state', String(30)),
    extend_existing=True,
)

affiliation = Table('affiliation', metadata,
    Column('id', Integer, primary_key=True),
    Column('user', Integer, ForeignKey('user.id', ondelete='CASCADE')),
    Column('institution', Integer, ForeignKey('institution.id', ondelete='CASCADE')),
    UniqueConstraint('user', 'institution', name='user_institution_unique'),
    extend_existing=True
)

tag = Table('tag', metadata,
    Column('id', Integer, primary_key=True),
    Column('tag', String, unique=True),
    extend_existing=True,
)

slide_tag = Table('slide_tag', metadata,
    Column('slide', Integer, ForeignKey('slide.id', ondelete='CASCADE')),
    Column('tag', Integer, ForeignKey('tag.id', ondelete='CASCADE')),
    PrimaryKeyConstraint('slide', 'tag', name='slide_tag_pk'),
    extend_existing=True
)

if __name__ == "__main__":
    engine_str = 'postgresql://{}:{}@{}:5432/{}'.format(
        DB['USER'], DB['PASSWORD'], DB['HOST'], DB['NAME'])
            
    engine = create_engine(engine_str)
    metadata.create_all(engine)

