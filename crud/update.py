from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, aliased
from sqlalchemy.orm.exc import NoResultFound
from threading import Thread
from werkzeug.exceptions import BadRequest
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash,check_password_hash
import sys
sys.path.insert(0, '../models/')


from models import Base,User,Filedetails
import datetime
import dbengine

DBSession=dbengine.get_object()


def rename_file(currentuser,data):
    """
    Function to update file name in db.
    """
    session=DBSession()
    try:
        filedetails=session.query(Filedetails).filter_by(fileid=data['fileid']).filter_by(userid=currentuser.userid).one()
        filedetails.filename=data['filerename']
        session.commit()
        session.close()
        return 'Successfully Uploaded'
    except NoResultFound:
        return 'You are not authorised to modify this file.'

def move_files(parentid, filelist, currentuser):
    """
    Function to update file name in db.
    """
    session=DBSession()
    try:
        files=session.query(Filedetails).filter(Filedetails.fileid.in_(filelist))

        for f in files:
             f.parentid = parentid

        session.commit()
        session.close()
        return 'Successfully Uploaded'
    except NoResultFound:
        return 'You are not authorised to modify this file.'
