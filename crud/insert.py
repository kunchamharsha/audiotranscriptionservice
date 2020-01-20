from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, aliased
from sqlalchemy.orm.exc import NoResultFound
from threading import Thread
from werkzeug.exceptions import BadRequest
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash,check_password_hash
import sys
import uuid
sys.path.insert(0, '../models/')


from models import Base,User,Filedetails,Transcriptiondata
import datetime

import dbengine

DBSession=dbengine.get_object()

def add_file(parentid,fileid,actualfilename,currentuser):
    """
    Function to store file data in db.
    """
    session=DBSession()
    if fileid == None:
        raise Exception('Invalid fileid')
    if actualfilename == None:
        raise Exception('Invalid filename')
    if currentuser.userid == None:
        raise Exception('Unauthorised User')
    try:
        filedetails=Filedetails(parentid=parentid,fileid=fileid,filename=actualfilename,fileuploadedon=datetime.datetime.now(),fileextension=actualfilename.split('.')[-1].lower(),filetype='f',userid=currentuser.userid)
        session.add(filedetails)
        session.commit()
        return 'Successfully Uploaded'
    except Exception as e:
        print(e)
        session.rollback()
        return 'Failed to add db to file'
    finally:
        session.close()

def create_folder(parentid,fileid,actualfilename,currentuser):
    """
    Function to store folder data in db.
    """
    session=DBSession()
    try:
        filedetails=Filedetails(parentid=parentid,fileid=fileid,filename=actualfilename,fileuploadedon=datetime.datetime.now(),fileextension=None,filetype='d',userid=currentuser.userid)
        session.add(filedetails)
        session.commit()
        return 'Successfully Created'
    except Exception as e:
        print(e)
        session.rollback()
        return 'Failed to add db to file'
    finally:
        session.close()

def add_transcribed_data(fileid,textdata):
    session=DBSession()
    if fileid==None or len(fileid)<36:
        raise Exception('Invalid file id')
    if textdata==None:
        raise Exception('Invalid response')
    try:
        textrecord=Transcriptiondata(id=str(uuid.uuid4()),fileid=fileid,response=textdata,status=True)
        session.add(textrecord)
        session.commit()
        return 'Successfully Added Transcription Data'
    except Exception as e:
        print(e)
        session.rollback()
        return 'Failed to add db to file'
    finally:
        session.close()