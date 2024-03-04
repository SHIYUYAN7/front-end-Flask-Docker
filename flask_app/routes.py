# Author: Prof. MM Ghassemi <ghassem3@msu.edu>
from flask import current_app as app
from flask import render_template, redirect, request, session, url_for
from flask import jsonify, copy_current_request_context
from flask_socketio import SocketIO, emit, join_room, leave_room, close_room, rooms, disconnect
from .utils.database.database import database
from werkzeug.datastructures import ImmutableMultiDict
from .utils.blockchain.blockchain import Block, Blockchain
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

@app.route('/signup')
def signup():
	return render_template('signup.html',user=getUser())

@app.route('/processsignup', methods = ["POST","GET"])
def processsignup():
	form_fields = dict((key, request.form.getlist(key)[0]) for key in list(request.form.keys()))
	result = db.createUser(form_fields['email'],form_fields['password'],form_fields['role'])
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
# MARKETPLACE RELATED
#######################################################################################
@app.route('/marketplace')
@login_required
def marketplace():
    return render_template('marketplace.html', user=getUser())

@app.route('/personal')
def personal():
    res = db.getUserWalletInfoByEmail(getUser())
    return render_template('personal.html',user=getUser(),personal=res)

@app.route('/admin')
def admin():
    all_transaction, all_blockchain = db.getAdminInfo()
    print(all_transaction, all_blockchain)
    return render_template('admin.html',user=getUser(),transactions= all_transaction,blockchain=all_blockchain)

@app.route('/buyer')
def buyer():
    res = db.getAllImages(getUser())
    return render_template('buyer.html',user=getUser() ,images = res)

@app.route('/seller')
def seller():
	res = db.getOwnImages(getUser())
	return render_template('seller.html', user=getUser(),images=res)

@app.route('/processCreateNFT', methods = ["POST","GET"])
def processCreateNFT():
	form_fields = dict((key, request.form.getlist(key)[0]) for key in list(request.form.keys()))

	result = db.createImage(getUser(),form_fields['description'],form_fields['token']);
	return json.dumps(result)

@app.route('/processUploadNFT', methods = ["POST","GET"])
def processUploadNFT():
	# description and token are in form_fields
	form_fields = dict((key, request.form.getlist(key)[0]) for key in list(request.form.keys()))
	# image they upload
	file = request.files['image']

	result = db.uploadImage(file, getUser(), form_fields['description'],form_fields['token'])
	return json.dumps(result)

@app.route('/processEditNFT', methods = ["POST","GET"])
def processEditNFT():
	form_fields = dict((key, request.form.getlist(key)[0]) for key in list(request.form.keys()))

	result = db.editImage(getUser(),form_fields['des'],form_fields['token'],form_fields['image_id']);
	return json.dumps(result)

@app.route('/processBuyNFT', methods = ["POST","GET"])
def processBuyNFT():
	# get image id
	form_fields = dict((key, request.form.getlist(key)[0]) for key in list(request.form.keys()))

	if not db.validTokenEnough(getUser(), form_fields['token']):
		return json.dumps({'fail':1})
	
	user_wallet,blockchain_wallet,last_chain_index,chain, new_transactions = db.getTransactionNeed(getUser(),form_fields['image_id'])

	# create a object to check
	blockchain = Blockchain(user_wallet, blockchain_wallet, last_chain_index, chain, new_transactions)

	infos = blockchain.mine_transaction()

	result = ""
	if infos != None:
		result = db.finishBought(infos, new_transactions)

	# print(user_wallet,blockchain_wallet,last_chain_index,chain,new_transactions)
	
	return json.dumps(result)

"""
@socketio.on('joined', namespace='/chat')
def joined(message):
    join_room('main')
    emit('status', {'msg': getUser() + ' has entered the room.', 'style': 'width: 100%;color:blue;text-align: right'}, room='main')

"""
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

