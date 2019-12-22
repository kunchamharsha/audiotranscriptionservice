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


engine = create_engine('sqlite:///crud/mynah.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)

def addfile(parentid,fileid,actualfilename,currentuser):
    """
    Function to store file data in db.
    """
    session=DBSession()
    filedetails=Filedetails(parentid=parentid,fileid=fileid,filename=actualfilename,fileuploadedon=datetime.datetime.now(),fileextension=actualfilename.split('.')[-1].lower(),filetype='f',userid=currentuser.userid)
    session.add(filedetails)
    session.commit()
    session.close()
    return 'Successfully Uploaded'

def createfolder(parentid,fileid,actualfilename,currentuser):
    """
    Function to store folder data in db.
    """
    session=DBSession()
    filedetails=Filedetails(parentid=parentid,fileid=fileid,filename=actualfilename,fileuploadedon=datetime.datetime.now(),fileextension=None,filetype='d',userid=currentuser.userid)
    session.add(filedetails)
    session.commit()
    session.close()
    return 'Successfully Created'

def AddTranscribedData(fileid,textdata):
    session=DBSession()
    textrecord=Transcriptiondata(id=str(uuid.uuid4()),fileid=fileid,response=textdata,status=True)
    session.add(textrecord)
    session.commit()
    session.close()
    return 'Successfully Added'