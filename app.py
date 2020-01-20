import sys
sys.path.insert(0,'./crud')
from flask import Flask, render_template,request,redirect,url_for,send_file,Response
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
import json
import uuid
import os
import registration
import read,insert,delete,update
from flask import jsonify
import re 
from models import User, Filedetails
from configuration.config import SECRET_KEY
from audio_converter import video_to_audio
import speech_to_text
#Initialising flask login manager
login_manager = LoginManager()
#Initialising Flask app
app=Flask(__name__,static_url_path='')

#################################### Flask Authorisation Initialisation ##################################


login_manager.init_app(app)
login_manager.login_view = "onboardingpage"
@login_manager.user_loader
def user_loader(id):
        user=registration.user_loader(id)
        return user
@login_manager.unauthorized_handler
def unauthorized_handler():
    return redirect(url_for('onboarding_page_with_notification',notification='Please login to gain access.'),code=302)

#################################### Template Rendering ##################################

@app.route('/')
def onboarding_page():
    """
    Function to render the onboarding page.
    """
    try:
        current_user.email
        return redirect(url_for('render_search_page'))
    except AttributeError:
        return render_template('registration.html')


@app.route('/login/<notification>')
def onboarding_page_with_notification(notification,register=False,error=None):
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
def render_registration_page():
    """
    Function to render the register page where the user is onboarded.
    """
    return render_template('registration.html')

@app.route('/search')
@login_required
def render_search_page():
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
            registration.register_user(data)
        except Exception as e:
            raise Exception('Email ID Exists')
        return render_template('registration.html',notification='Registered successfully please login.')
    except Exception as e:
        print e
        return render_template('registration.html',error=str(e),register=True)

@app.route('/api/authenticate', methods=['POST'])
def login_authorisation():
    """
    Function to authorise a username and password against the credentials
    present in the database and redirect the user to home page.
    """
    user = registration.authenticate_user(request.form)
    if user == None:
        return render_template('registration.html', error='Invalid credentials. Please enter correct details.')
    elif isinstance(user, unicode) != True:
        login_user(user)
        return redirect(url_for('render_search_page'))
    else:
        return render_template('registration.html')

@app.route("/api/logout")
@login_required
def logout_page():
    """
    Function to logout user and redirect them to the login page.
    """
    logout_user()
    return redirect("/",302)


@app.route('/api/returnfiles',methods=['GET'])
@login_required
def return_files():
    """
    Function to return list of files uploaded by the user.
    """
    return read.list_of_files_uploaded(current_user)

@app.route('/api/listaudiodata',methods=['POST'])
@login_required
def get_children():
    """
    Function to return list of files uploaded by the user.
    """
    data=json.loads(request.data)
    return read.audio_data(current_user)

@app.route('/api/getdescendents',methods=['POST'])
@login_required
def get_descendents():
    """
    Function to return list of files uploaded by the user.
    """
    data=json.loads(request.data)
    return read.get_descendents(data["folderid"], current_user)

@app.route('/api/rename',methods=['POST'])
@login_required
def rename_file():
    """
    Function to rename a file.
    """
    data=json.loads(request.data)
    try:
        return update.rename_file(current_user,data)
    except Exception as e:
        print(str(e))
        return Response(str(e),422)

@app.route('/api/deletefile',methods=['GET'])
@login_required
def delete_file():
    """
    Function to delete a file by fileid
    """
    fileid=request.args.get('id')
    if fileid==None or fileid=='':
        raise Exception('Invalid fileid')
    return delete.delete_file(fileid,current_user)



@app.route('/api/upload',methods=['POST'])
@login_required
def new_file_upload():
    """
    function to upload mp4 files to server.
    """
    if request.files:
        reqlen=len(request.files)
        for i in xrange(reqlen):
            files = request.files['files['+str(i)+']']
            if files and allowed_file(files.filename):
                parentid = request.form['parentid']
                actualfilename=files.filename
                fileid = str(uuid.uuid4())
                filename= fileid+'.mp4'
                filepath=os.path.join(app.config['UPLOAD_FOLDER'],filename)
                files.save(filepath)
                try:
                    insert.add_file(parentid,fileid,actualfilename,current_user)
                except Exception as e:
                    print(str(e))
                    return Response('Could not upload file, Please Retry Again.')
                audio_file_path=video_to_audio(filepath)
                transcribe_data=speech_to_text.convert(audio_file_path)
                try:
                    insert.add_transcribed_data(fileid,transcribe_data)
                except Exception as e:
                    print(str(e))
                    return Response('Could not add Transcribed Data')
            else:
                return Response("Invalid File Format, Please upload mp4", status=422)
        return 'Successfully uploaded files'
    else:
        return 'No file Uploaded'
    #return json.dumps(insert.addnewpost(request.data,actualfilename,current_user))



################################################################

@app.route('/cdn/<fileid>',methods=['GET'])
@login_required
def get_file(fileid):
    """
    Function to check access of a user to a given function.
    """
    filedata=read.check_access(fileid,current_user)
    if filedata['access_state']==1:
        return send_file('static/fileuploadfolder/'+fileid+'.mp4', attachment_filename=filedata['filename'])
    elif filedata['access_state']==0:
        return Response('Access Denied',422)

@app.route('/api/transcriptiondata/',methods=['GET'])
def get_data():
    """
    API for transcriptiondata.
    """
    fileid=request.args.get('fileid')
    sort=request.args.get('sortby')
    apitoken=request.args.get('apitoken')
    order=request.args.get('order')
    try:
        data=read.api_data(apitoken,fileid,sort,order)
    except Exception as e:
        return Response(e,401)
    return jsonify(data)

@app.route('/getapitoken',methods=['GET'])
@login_required
def get_api_token():
    """
    Function to return the api token of a user. 
    """
    return json.dumps({'apitoken':current_user.apitoken,'endpointurl':'/api/transcriptiondata','Optional params':{'fileid':'fileid','sortby':['created_date'],'order':['asc','desc']}})

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']




APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'static/fileuploadfolder/')
app.config['MAX_CONTENT_LENGTH'] = 7 * 1024 * 1024
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = set(['mp4'])
app.config['static_url_path'] ='/static'
app.config['SECRET_KEY'] = SECRET_KEY

if __name__=='__main__':
    app.run('0.0.0.0',debug=True)
