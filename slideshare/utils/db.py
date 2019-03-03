from sqlalchemy.sql import select
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime


def get_or_create(conn, obj, table, condition):
    try:
        s = select([table]).where(condition)
        r = conn.execute(s).first()
        if r:
            pk = r.id
        else:
            pk = conn.execute(table.insert(), **obj).inserted_primary_key[0]
    except SQLAlchemyError as e:
        # TODO log error
        if 'unique constraint' in message: # could cause inf loop
           pk = get_or_create(conn, obj, table, condition)
    return pk

def execute_query(conn, query, params, transform=None, unique=False):
    '''
    Executes query. Converts datetime objects to strings
    for json serialization. 

    Args:
        conn:       engine or connection object. (if connection is passed, transaction
                    can be rolled back by the caller)
        query:      sql query in string format
        params:     string parameters for query string
        transform:  a callable that accepts a mutable, subsriptable object and returns a
                    modified object of the same type
        unique:     boolean. Returns a single object. 
    Returns:
        List of dicts if unique=False, else a single dict, and an http status code. 
        In case of exception, returns empty dict and 500 code.

    Notes:
        - convoluted code to convert datetime to strings for json serialization
    '''
    code = 200
    res = []

    checked = 0
    datetime_columns = []
    try:
        for row in conn.execute(query, params):
            row = dict(row)
            if not checked:
                datetime_columns = [key for key in row.keys() if type(row[key]) == datetime]
                checked = 1
            for col in datetime_columns:
                row[col] = str(row[col])

            if transform:
                res.append(transform(row))
            else:
                res.append(row)       
        else:
            if unique: res = res[0]
    except Exception as e:
        print(e)
        code = 500
    
    return res, code
