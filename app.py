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
from functions import get_10tweets
import pandas as pd
import re 
#import plotly.graph_objs as go
#import dash
#import dash_core_components as dcc
#import dash_html_components as html
import os

#This is the web main page 
app = Flask(__name__)


@app.route('/')
def index():
 
  return redirect(url_for('login'))

if __name__ == '__main__':
    app.run()
    
@app.route('/faqs', methods=['GET', 'POST'])
def get_info():
    return render_template('faqs.html')
   
    
@app.route('/prediction', methods=['GET', 'POST'])
@login_required
def prediction_submit():
  """Provide HTML form to submit a prediction."""
  form = PredictionForm(request.form)
  if request.method == 'POST' and form.validate():
      #whatever we do with text etc
      text = form.text.data
      return redirect(url_for('prediction_made',text=text))
  return render_template('prediction/submit.html', form=form)

@app.route('/prediction/aftermath/<text>',methods = ['GET','POST'])
@login_required
def prediction_made(text):
    #It should be a button that send us back to prediction
    df = pd.DataFrame()
    df = get_10tweets(current_user.username)
    
    RT_mean = df["RT_l10"][0]
    FAV_mean = df["FC_l10"][0]
    
    if RT_mean > RT_mean:
        RT_text = 'prediction over average'
    else:
        RT_text = 'prediction under average'
    if (FAV_mean > FAV_mean):
        FAV_text = 'prediction over average'
    else:
        FAV_text = 'prediction under average'
    has = ''
    for m in re.finditer(r"#\w+", text): 
        w = m.group(0)
        w = w.strip('#') 
        has+= w
        has+= ','
            
    # text = request.args.get('text')
    # some response showing the number of RT/FAVS
    return render_template('prediction/aftermath.html', RT=RT_mean, FAV=FAV_mean, text=text, RTaa=RT_text, FAVaa=FAV_text,hashtags = has)



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
    
    #Authentication
    auth = tweepy.OAuthHandler(os.environ['consumer_key'],os.environ['consumer_secret'])
    auth.set_access_token(os.environ['access_key'], os.environ['access_secret'])
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
