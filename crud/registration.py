from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, aliased
from sqlalchemy.orm.exc import NoResultFound
import sys
from werkzeug.security import generate_password_hash,check_password_hash
import uuid
import os
sys.path.insert(0,'./models')
from models import Base,User,Filedetails
from binascii import hexlify
import dbengine


DBSession=dbengine.get_object()


def authenticate_user(loginformdata):  # loginverification
    """
    Function to authenticate user against the credentials saved in database.
    """
    session = DBSession()
    try:
        user = session.query(User).filter_by(email=loginformdata['email']).one()
    except NoResultFound, e:
        session.close()
        return None
    try:
        if user.password:
            if check_password_hash(user.password,loginformdata['password']):
                user.authenticated = True
                return user
            return None
        session.close()
        return None
    except Exception, e:
        return None
    finally:
        session.close()


def user_loader(user_id):
    session = DBSession()
    """Given *user_id*, return the associated User object.

    :param unicode user_id: user_id (email) user to retrieve
    """
    try:
        user = session.query(User).filter_by(userid=user_id).one()
        return user
    except NoResultFound:
        return None
    finally:
        session.close()

def generateapitoken():
    key=hexlify(os.urandom(12))
    return key

def register_user(signupformdata):
    """
    Function to onboard a user on to the database. 
    """
    session = DBSession()
    try:
        user = User(email=signupformdata['email'], userid=str(uuid.uuid4()), password=generate_password_hash(signupformdata['pwd']),apitoken=generateapitoken())
        session.add(user)
        session.commit()
        return 'successful'
    except Exception as e:
        raise Exception(str(e))
    finally:
        session.close()