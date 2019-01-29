from sqlalchemy.sql import select
from sqlalchemy.exc import SQLAlchemyError

def get_or_create(db_engine, obj, table, condition):
    try:
        s = select([table]).where(condition)
        r = db_engine.execute(s).first()
        if not r:
            r = db_engine.execute(table.insert(), **obj).inserted_primary_key[0]
        pk = r.id
    except SQLAlchemyError as e:
        # TODO log error
        if 'unique constraint' in message: # could cause inf loop
           pk = get_or_create(db_engine, obj, table, condition)
    return pk
