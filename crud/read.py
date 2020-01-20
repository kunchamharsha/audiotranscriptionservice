from threading import Thread
from werkzeug.exceptions import BadRequest
from werkzeug.security import generate_password_hash,check_password_hash
import sys
from flask import jsonify
sys.path.insert(0, '../models/')
from models import Base,User,Filedetails,Transcriptiondata
import datetime
import dbengine

DBSession=dbengine.get_object()

def list_of_files_uploaded(currentuser):
    """
    Function to return list of files uploaded by a user.
    """
    session=DBSession()
    try:
        files=session.query(Filedetails,Transcriptiondata).filter(Filedetails.fileid==Transcriptiondata.id).filter_by(userid=currentuser.userid)
        listoffiles=[]
        for i in files:
            filedata={}
            filedata['fileid']      =i.fileid
            filedata['parentid']    =i.parentid
            filedata['filename']    =i.filename
            filedata['filetype']    =i.fileextension
            filedata['Upload date'] =i.fileuploadedon
            filedata['response']    =i.response
            listoffiles.append(filedata)
        return jsonify(listoffiles)
    except Exception as e:
        print(str(e))
        raise('Could not query the DB')
    finally:
        session.close()

def audio_data(folderid, currentuser):
    """
    Function to return list of files under given folder.
    """
    session=DBSession()
    try:
        files=session.query(Filedetails,Transcriptiondata).filter(Filedetails.userid==currentuser.userid).filter(Filedetails.fileid==Transcriptiondata.fileid)
        listoffiles=[]
        for row in files:
            filesdata=row[0]
            transdata=row[1]
            filedata={}
            filedata['fileid']      =filesdata.fileid
            filedata['filename']    =filesdata.filename
            filedata['parentid']    =filesdata.parentid
            filedata['fileext']     =filesdata.fileextension
            filedata['filetype']    =filesdata.filetype
            filedata['upload_date'] =filesdata.fileuploadedon
            filedata['response']    =transdata.response
            listoffiles.append(filedata)
        return jsonify(listoffiles)
    except Exception as e:
        print(str(e))
        raise Exception('Could not query the database')
    finally:
        session.close()

def api_data(apitoken,fileid=None,sort=None,order=None):
    """
    Get API data.
    """
    session=DBSession()
    try:
        userid=session.query(User.userid).filter_by(apitoken=apitoken).one()
    except NoResultFound:
        raise Exception('Invalid Token')
    try:
        files=session.query(Filedetails,Transcriptiondata).filter(Filedetails.fileid==Transcriptiondata.fileid).filter(Filedetails.userid==userid[0])
        if fileid!=None:
            files=files.filter(Filedetails.fileid==fileid)
        if sort!=None:
            if sort=='created_date':
                if order!=None:
                    if order=='asc':
                        files=files.order_by(Filedetails.fileuploadedon)
                    else:
                        files=files.order_by(desc(Filedetails.fileuploadedon))
                else:
                    files=files.order_by(Filedetails.fileuploadedon)
        listoffiles=[]    
        for row in files:
            filesdata=row[0]
            transdata=row[1]
            filedata={}
            filedata['fileid']      =filesdata.fileid
            filedata['filename']    =filesdata.filename
            filedata['parentid']    =filesdata.parentid
            filedata['fileext']     =filesdata.fileextension
            filedata['filetype']    =filesdata.filetype
            filedata['upload_date'] =filesdata.fileuploadedon
            filedata['response']    =transdata.response
            listoffiles.append(filedata)
        return listoffiles
    except Exception:
        raise Exception('DB query Failed')
    finally:
        session.close()


def check_access(fileid,currentuser):
    """
    Function to check users access to the requested file.
    """
    session=DBSession()
    returnfiledata={}
    try:
        filedata=session.query(Filedetails).filter_by(userid=currentuser.userid).filter_by(fileid=fileid).one()
        returnfiledata['fileid']=filedata.fileid
        returnfiledata['filename']=filedata.filename
        returnfiledata['access_state']=1
        return returnfiledata
    except NoResultFound:
        returnfiledata['access_state']=0
        return returnfiledata
    finally:
        session.close()