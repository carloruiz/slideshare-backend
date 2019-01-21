"""create db tables

Revision ID: 798b7b982ec3
Revises: 
Create Date: 2019-01-20 21:52:29.528047

"""
from alembic import op
from sqlalchemy import (
    Table, MetaData, Column, 
    Integer, String, ForeignKey, 
    DateTime, UniqueConstraint,
    PrimaryKeyConstraint, create_engine
)
from datetime import datetime, timezone

# revision identifiers, used by Alembic.
revision = '798b7b982ec3'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('user',
        Column('id', Integer, primary_key=True),
        Column('username', String(15), unique=True),
        Column('email', String, unique=True),
        Column('password', String)
    )

    op.create_table('user_meta',
        Column('id', Integer, primary_key=True),
        Column('userid', Integer, ForeignKey('user.id', ondelete="SET NULL"), unique=True), 
        Column('joined_on', DateTime, default=datetime.now(timezone.utc)),
        Column('last_login', DateTime, default=datetime.now(timezone.utc)),
        Column('user_type', String(15)),
        extend_existing=True,
    )

    op.create_table('slide',
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

    op.create_table('institution',
        Column('id', Integer, primary_key=True),
        Column('name', String),
        Column('state', String(30)),
        extend_existing=True,
    )

    op.create_table('affiliation',
        Column('id', Integer, primary_key=True),
        Column('user', Integer, ForeignKey('user.id', ondelete='CASCADE')),
        Column('institution', Integer, ForeignKey('institution.id', ondelete='CASCADE')),
        UniqueConstraint('user', 'institution', name='user_institution_unique'),
        extend_existing=True
    )

    op.create_table('tag',
        Column('id', Integer, primary_key=True),
        Column('tag', String, unique=True),
        extend_existing=True,
    )

    op.create_table('slide_tag', 
        Column('slide', Integer, ForeignKey('slide.id', ondelete='CASCADE')),
        Column('tag', Integer, ForeignKey('tag.id', ondelete='CASCADE')),
        PrimaryKeyConstraint('slide', 'tag', name='slide_tag_pk'),
        extend_existing=True
    )


def downgrade():
    pass
