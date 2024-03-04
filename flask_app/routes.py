# Author: Prof. MM Ghassemi <ghassem3@msu.edu>
from flask import current_app as app
from flask import render_template, redirect, request, session, url_for, copy_current_request_context
from flask_socketio import SocketIO, emit, join_room, leave_room, close_room, rooms, disconnect
from .utils.database.database  import database
from werkzeug.datastructures   import ImmutableMultiDict
from pprint import pprint
import json
import random
import functools
from . import socketio
db = database()


#######################################################################################
# AUTHENTICATION RELATED
#######################################################################################
def login_required(func):
    @functools.wraps(func)
    def secure_function(*args, **kwargs):
        if "email" not in session:
            return redirect(url_for("login", next=request.url))
        return func(*args, **kwargs)
    return secure_function

def getUser():
	if 'email' in session:
		return db.reversibleEncrypt('decrypt', session['email'])
	else:
		return 'Unknown'

@app.route('/login')
def login():
	return render_template('login.html',user=getUser())

@app.route('/logout')
def logout():
	session.pop('email', default=None)
	return redirect('/')

@app.route('/processlogin', methods = ["POST","GET"])
def processlogin():
	form_fields = dict((key, request.form.getlist(key)[0]) for key in list(request.form.keys()))
	
	result = db.authenticate(form_fields['email'],form_fields['password'])
	if result.get('success'):
		session['email'] = db.reversibleEncrypt('encrypt', form_fields['email']) 

	return json.dumps(result)

	
#######################################################################################
# CHATROOM RELATED
#######################################################################################
@app.route('/chat')
@login_required
def chat():
    return render_template('chat.html', user=getUser())

@socketio.on('joined', namespace='/chat')
def joined(message):
	join_room('main')

	role = db.getRole(getUser())
	if role[0]['role'] == 'owner':
	 	emit('status', {'msg': getUser() + ' has entered the room.', 'style': 'width: 100%;color:blue;text-align: right'}, room='main')
	else:
	 	emit('status', {'msg': getUser() + ' has entered the room.', 'style': 'width: 100%;color:grey;text-align: left'}, room='main')

@socketio.on('send_message', namespace='/chat')
def send_message(message):
	role = db.getRole(getUser())
	if role[0]['role'] == 'owner':
		emit('update_message', {'msg': message['msg'], 'style': 'width: 100%;color:blue;text-align: right'}, room='main')
	else:
		emit('update_message', {'msg': message['msg'], 'style': 'width: 100%;color:grey;text-align: left'}, room='main')

@socketio.on('leave_chat', namespace='/chat')
def leave_chat(message):
	leave_room('main')
	role = db.getRole(getUser())
	if role[0]['role'] == 'owner':
		emit('update_message', {'msg': getUser() + ' has left the room.', 'style': 'width: 100%;color:blue;text-align: right'}, room='main')
	else:
		emit('update_message', {'msg': getUser() + ' has left the room.', 'style': 'width: 100%;color:grey;text-align: left'}, room='main')

#######################################################################################
# OTHER
#######################################################################################
@app.route('/')
def root():
	return redirect('/home')

@app.route('/home')
def home():
	print(db.query('SELECT * FROM users'))
	x     = random.choice(['I am a crazy fan of Neon Genesis Evangelion!','I love fried pork chops!','I am obsessed with Lego cars!'])
	return render_template('home.html', user=getUser(), fun_fact = x)

@app.route('/projects')
def projects():
    return render_template('projects.html',user=getUser())

@app.route('/piano')
def piano():
    return render_template('piano.html',user=getUser())

@app.route('/resume')
def resume():
	resume_data = db.getResumeData()
	# pprint(resume_data)
	return render_template('resume.html', user=getUser(), resume_data = resume_data)

@app.route('/processfeedback', methods = ['POST'])
def processfeedback():
	feedback = request.form
	feedback_list = [feedback.get('name'),feedback.get('email'),feedback.get('comment')]
	result = db.updateFeedback(feedback_list)

	return render_template('processfeedback.html',user=getUser(),feedback_data = result)

@app.route("/static/<path:path>")
def static_dir(path):
    return send_from_directory("static", path)

@app.after_request
def add_header(r):
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, public, max-age=0"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    return r
