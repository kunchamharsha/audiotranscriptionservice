from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, aliased
from sqlalchemy.orm.exc import NoResultFound
from threading import Thread
from werkzeug.exceptions import BadRequest
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash,check_password_hash
import read
import sys
sys.path.insert(0, '../models/')
import os

from models import User,Filedetails
import datetime
import dbengine

DBSession=dbengine.get_object()

def delete_file(fileid,currentuser):
    """
    Function to delete a file by file id. 
    """
    session=DBSession()
    try:
        filedetails = session.query(Filedetails).filter_by(fileid=fileid).filter_by(userid=currentuser.userid).one()
        session.delete(filedetails)
        session.commit()
        return 'Successfully deleted'
    except Exception as err:
        print err
        return 'Deletion Failed'
    finally:
        session.close()
