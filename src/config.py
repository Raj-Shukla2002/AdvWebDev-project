# utils.py
import jwt
import bcrypt
from flask import current_app
import datetime

PEPPER = b'supersecretpepper'

def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password + PEPPER, salt)
    return hashed_password, salt

def verify_password(password, stored_hashed_password, stored_salt):
    hashed_password = bcrypt.hashpw(password + PEPPER, stored_salt)
    return hashed_password == stored_hashed_password

def create_jwt(username):
    payload = {
        'sub': username,
        'iat': datetime.datetime.utcnow(),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30),
    }
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')

def decode_jwt(token):
    try:
        return jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
