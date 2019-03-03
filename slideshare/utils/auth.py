from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (
    TimedJSONWebSignatureSerializer as Serializer, 
    BadSignature, 
    SignatureExpired
)
from slideshare.db import db_engine
import os


def hash_password(password):
    return pwd_context.encrypt(password)

def verify_password(credentials, password):
    return pwd_context.verify(password, credentials.password)

# tokens expire in 12 hours
def generate_auth_token(userid, expiration = 60*60*12):
    s = Serializer(os.environ['SECRET_KEY'], expires_in=expiration)
    return s.dumps({ 'id': userid })

def verify_auth_token(token):
    s = Serializer(os.environ(['SECRET_KEY']))
    try:
        data = s.loads(token)
    except  SignatureExpired:
        return None # valid token, but expired
    except BadSignature:
        return None # invalid token
    userid = data.get(data['id'])
    return userid
