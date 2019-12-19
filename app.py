import sys
sys.path.insert(0,'./crud')

from flask import Flask, render_template,request,redirect,url_for,send_file,Response
from flask_login import LoginManager, login_required, login_user, logout_user, current_user

from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
import json


from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker,scoped_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.sqlite import TEXT
from sqlalchemy.sql.expression import delete
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.pool import SingletonThreadPool
import uuid
import os
import registration
import read,insert,delete,update

import re 


from models import User, Filedetails
from config import SECRET_KEY


#Initialising flask login manager
login_manager = LoginManager()

#Initialising Flask app
app=Flask(__name__,static_url_path='')
admin = Admin(app)



engine = create_engine('sqlite:///crud/beeruva.db',poolclass=SingletonThreadPool)
Base = declarative_base()
session= scoped_session(sessionmaker(bind=engine))

admin.add_view(ModelView(User, session))
admin.add_view(ModelView(Filedetails, session))






login_manager.init_app(app)
login_manager.login_view = "onboardingpage"



@login_manager.user_loader
def user_loader(id):
        user=registration.user_loader(id)
        return user

@login_manager.unauthorized_handler
def unauthorized_handler():
    return redirect(url_for('onboardingpagewithnotification',notification='Please login to gain access.'),code=302)

#################################### Template Rendering ##################################

@app.route('/')
def onboardingpage():
    """
    Function to render the onboarding page.
    """
    try:
        current_user.email
        return redirect(url_for('render_searchpage'))
    except AttributeError:
        return render_template('registration.html')


@app.route('/login/<notification>')
def onboardingpagewithnotification(notification,register=False,error=None):
    """
    Function to render a login page with a notification
    """
    try:
        current_user.email
        return redirect(url_for('home'))
    except AttributeError:
        if notification==None:
            notification='Please login to gain access!'
        return render_template('registration.html',error='',notification=notification,register=True)


@app.route('/register')
def render_registrationpage():
    """
    Function to render the register page where the user is onboarded.
    """
    return render_template('registration.html')

@app.route('/search')
@login_required
def render_searchpage():
    """
    Function to render the search page.
    """
    return render_template('search.html')



#################################### API Endpoints  ################################################






@app.route('/api/register', methods=["POST"])
def register_user():
    """
    Function to onboard the user on to the application.
    """
    try:
        data=request.form
        print(data)
        if data['email'] == '':
            raise Exception('Enter Email ID')
        else:
            regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
            if (re.search(regex,data['email'])) == None:  
                raise Exception("Invalid Email ID, Please enter correct Email ID")  
        if data['pwd'] == '':
            raise Exception('Enter Password')
        else:
            if len(data['pwd'])<6:
                raise Exception('Password too short')
        try:
            registration.registeruser(data)
        except Exception as e:
            raise Exception('Email ID Exists')
        return render_template('registration.html',notification='Registered successfully please login.')
    except Exception as e:
        print e
        return render_template('registration.html',error=str(e),register=True)

@app.route('/api/authenticate', methods=['POST'])
def loginauthorisation():
    """
    Function to authorise a username and password against the credentials
    present in the database and redirect the user to home page.
    """
    print request.form
    user = registration.authenticateuser(request.form)
    if user == None:
        return render_template('registration.html', error='Invalid credentials. Please enter correct details.')
    elif isinstance(user, unicode) != True:
        login_user(user)
        return redirect(url_for('render_searchpage'))


@app.route("/api/logout")
@login_required
def logoutpage():
    """
    Function to logout user and redirect them to the login page.
    """
    logout_user()
    return redirect("/",302)


@app.route('/api/returnfiles',methods=['GET'])
@login_required
def returnfiles():
    """
    Function to return list of files uploaded by the user.
    """
    return read.listofilesuploaded(current_user)

@app.route('/api/getchildren',methods=['POST'])
@login_required
def getchildren():
    """
    Function to return list of files uploaded by the user.
    """
    data=json.loads(request.data)
    return read.getchildren(data["folderid"], current_user)

@app.route('/api/getdescendents',methods=['POST'])
@login_required
def getdescendents():
    """
    Function to return list of files uploaded by the user.
    """
    data=json.loads(request.data)
    return read.getdescendents(data["folderid"], current_user)

@app.route('/api/rename',methods=['POST'])
@login_required
def renamefile():
    """
    Function to rename a file.
    """
    data=json.loads(request.data)
    return update.renamefile(current_user,data)


@app.route('/api/deletefile',methods=['GET'])
@login_required
def deletefile():
    """
    Function to delete a file by fileid
    """
    fileid=request.args.get('id')
    return delete.deletefile(fileid,current_user)



@app.route('/api/upload',methods=['POST'])
@login_required
def newfileupload():
    """
    function to upload mp4 files to server.
    """

    parentid = request.form['parentid']

    if request.files:
        reqlen=len(request.files)
        for i in xrange(reqlen):
            print request.files
            files = request.files['files['+str(i)+']']
            print files
            if files and allowed_file(files.filename):
                actualfilename=files.filename
                filename = str(uuid.uuid4())+'.mp4'
                files.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
                try:
                    json.dumps(insert.addfile(parentid,filename,actualfilename,current_user))
                except Exception as e:
                    print e
                    print 'invalid'
            else:
                return Response("Invalid File Format, Please upload mp4", status=422)
        return 'Successfully uploaded files'
    else:
        return 'No file Uploaded'
    #return json.dumps(insert.addnewpost(request.data,actualfilename,current_user))



################################################################

@app.route('/cdn/<fileid>',methods=['GET'])
@login_required
def getfile(fileid):
    """
    Function to check access of a user to a given function.
    """
    filedata=read.check_access(fileid,current_user)
    if filedata['access_state']==1:
        return send_file('static/fileuploadfolder/'+fileid, attachment_filename=filedata['filename'])
    elif filedata['access_state']==0:
        return 'Access Denied'



def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']




APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'static/fileuploadfolder/')
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = set(['mp4'])
app.config['static_url_path'] ='/static'
app.config['SECRET_KEY'] = SECRET_KEY

if __name__=='__main__':
    app.run('0.0.0.0',debug=True)
