from datetime import datetime, timezone
import os
from config import config
from sqlalchemy import (
    Table, MetaData, Column, 
    Integer, String, ForeignKey, 
    DateTime, UniqueConstraint,
    PrimaryKeyConstraint, create_engine
)

metadata = MetaData()

user = Table('user', metadata,
    Column('id', Integer, primary_key=True),
    Column('username', String(15), unique=True, nullable=False),
    Column('email', String, unique=True, nullable=False),
    Column('password', String, nullable=False),
    extend_existing=True,
)

user_meta = Table('user_meta', metadata,
    Column('id', Integer, primary_key=True),
    Column('userid', Integer, ForeignKey('user.id', ondelete="SET NULL"), unique=True), 
    Column('firstname', String(30)),
    Column('lastname', String(30)),
    Column('joined_on', DateTime, default=datetime.now(timezone.utc)),
    Column('last_login', DateTime, default=datetime.now(timezone.utc)),
    Column('user_type', String(15)),
    extend_existing=True,
)

slide_id = Table('slide_id', metadata,
    Column('id', Integer, primary_key=True),
    extend_existing=True
)
slide = Table('slide', metadata,
    Column('id', Integer, ForeignKey('slide_id.id', ondelete='CASCADE'), primary_key=True),
    Column('title', String(30), nullable=False),
    Column('url', String, unique=True, nullable=False),
    Column('userid', Integer, ForeignKey('user.id', ondelete='CASCADE')),
    Column('username', String(15), ForeignKey('user.username', 
        onupdate='CASCADE', ondelete='CASCADE')),
    Column('size', String(20), nullable=False),
    Column('description', String),
    Column('created_on', DateTime, default=datetime.now(timezone.utc)),
    Column('last_mod', DateTime, default=datetime.now(timezone.utc)),
    Column('pdf', String, unique=True, nullable=False),
    Column('thumbnail', String, unique=True, nullable=False),
    UniqueConstraint('userid', 'title', name='unique_userid_title'),
    extend_existing=True
)

institution = Table('institution', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String, nullable=False),
    Column('state', String(30), nullable=False),
    UniqueConstraint('name', 'state', name='name_state_unique'),
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
    Column('tag', String, unique=True, nullable=False),
    extend_existing=True,
)

slide_tag = Table('slide_tag', metadata,
    Column('slide', Integer, ForeignKey('slide_id.id', ondelete='CASCADE')),
    Column('tag', Integer, ForeignKey('tag.id', ondelete='CASCADE')),
    PrimaryKeyConstraint('slide', 'tag', name='slide_tag_pk'),
    extend_existing=True
)

if __name__ == "__main__":
    engine = create_engine(config['DB_URI'])
    metadata.create_all(engine)

