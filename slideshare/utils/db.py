from sqlalchemy.sql import select
from sqlalchemy.exc import SQLAlchemyError

def get_or_create(db_engine, obj, table, condition):
    try:
        s = select([table]).where(condition)
        r = db_engine.execute(s).first()
        if r:
            pk = r.id
        else:
            pk = db_engine.execute(table.insert(), **obj).inserted_primary_key[0]
    except SQLAlchemyError as e:
        # TODO log error
        if 'unique constraint' in message: # could cause inf loop
           pk = get_or_create(db_engine, obj, table, condition)
    return pk

def execute_query(db_engine, query, params, transform=None, unique=False):
    code = 200
    try:
        if transform:
            res = [transform(dict(row)) for row in db_engine.execute(query, params)]
        else:
            res = [dict(row) for row in db_engine.execute(query, params)]
            
        if len(res) == 0:
            code = 204
        else:
            if unique: res = res[0]
    except Exception as e:
        print(e)
        res, code = {}, 500
    
    return res, code
