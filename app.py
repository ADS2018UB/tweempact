# -*- coding: utf-8 -*-
"""
Created on Wed Oct 31 17:47:45 2018

@author: PC
"""
from flask import Flask, make_response,request 
from flask_pymongo import PyMongo
from flask import abort, jsonify, redirect, render_template
from flask import url_for
from flask_login import LoginManager, current_user
from flask_login import login_user, logout_user
from flask_login import login_required
from models import User
from forms import PredictionForm,LoginForm
import tweepy

#This is the web main page 
app = Flask(__name__)
#app.config['MONGO_DBNAME'] = 'foodb'
#app.config['MONGO_URI'] = 'mongodb://localhost:27017/foodb'
#mongo = PyMongo(app)




@app.route('/')
def index():
 
  return redirect(url_for('login'))

if __name__ == '__main__':
    app.run()
    
    
    
@app.route('/prediction', methods=['GET', 'POST'])
@login_required
def prediction_submit():
  """Provide HTML form to submit a prediction."""
  form = PredictionForm(request.form)
  if request.method == 'POST' and form.validate():
      #whatever we do with text etc
      return redirect(url_for('prediction_made'))
  return render_template('prediction/submit.html', form=form)

@app.route('/prediction/aftermath',methods = ['GET','POST'])
@login_required
def prediction_made():
    #It should be a button that send us back to prediction
    
    #some response showing the number of RT/FAVS
    return render_template('prediction/aftermath.html')


@app.route('/evolution')
@login_required
def historic():


    return render_template('dashboard/trial.html')

app.config['SECRET_KEY'] = 'esydM2ANhdcoKwdVa0jWvEsbPFuQpMjg' # Create your own.
app.config['SESSION_PROTECTION'] = 'strong'
login_manager = LoginManager()
login_manager.setup_app(app)
login_manager.login_view = 'login'

#@login_manager.user_loader
#def load_user(user_id):
 # """Flask-Login hook to load a User instance from ID."""
  #u = mongo.db.users.find_one({"username": user_id})
  #if not u:
   #   return None
  #return User(u['username'])

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

@app.route('/login/', methods=['GET', 'POST'])
def login():
  if current_user.is_authenticated:
    return redirect(url_for('prediction_submit'))
  form = LoginForm(request.form)
  error = None
  if request.method == 'POST' and form.validate():
    username = form.username.data.lower().strip()
    #password = form.password.data.lower().strip()
    # user = username
    with open('consumer_key.txt', 'r') as f:
        consumer_key =  f.read()
    f.closed
    
    with open('consumer_secret.txt', 'r') as f:
        consumer_secret = f.read()
    f.closed
    
    with open('access_key.txt', 'r') as f:
        access_key = f.read()
    f.closed
    
    with open('access_secret.txt', 'r') as f:
         access_secret = f.read()
    f.closed
    
    
    #Authentication
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth)

    try:
        user = api.get_user(id=username)
    
    except tweepy.TweepError :
        user = False
    #We need to substitute this for a line that actually looks inside twitter
    #user = mongo.db.users.find_one({"username": form.username.data})
    
    if user : #and User.validate_login(user['password'], form.password.data):  
      user_obj = User(username)#['username'])
      login_user(user_obj)
      return redirect(url_for('prediction_submit'))
    else:
      error = 'Incorrect twitter username'# or password.'
  return render_template('login.html',
      form=form, error=error)

@app.route('/logout/')
def logout():
  logout_user()
  return redirect(url_for('login'))
