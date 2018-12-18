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
from functions import get_10tweets,get_TT, get_plot_images
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
  Trending = get_TT()
  form = PredictionForm(request.form)
  if request.method == 'POST' and form.validate():
      #whatever we do with text etc
      text = form.text.data
      return redirect(url_for('prediction_made',text=text))
  return render_template('prediction/submit.html', form=form , TT = Trending)

@app.route('/prediction/aftermath/<text>',methods = ['GET','POST'])
@login_required
def prediction_made(text):
    #It should be a button that send us back to prediction
    df = pd.DataFrame()
    df = get_10tweets(current_user.username)
    
    RT_mean = df["RT_l10"][0]
    FAV_mean = df["FC_l10"][0]
    
    rt_bool = RT_mean >= RT_mean
    fv_bool = FAV_mean >= FAV_mean
    if rt_bool:
        RT_text = 'Great job!'
    else:
        RT_text = ''
    if fv_bool:
        FAV_text = 'Great job!'
    else:
        FAV_text = ''
    
    has = ''
    for m in re.finditer(r"#\w+", text): 
        w = m.group(0)
        w = w.strip('#') 
        has+= w
        has+= ','
    has = has[:-1]    
    no_has = ''
    for m in re.finditer(r"\s\w+", text):
        w = m.group(0)
        no_has+= w
           
    # text = request.args.get('text')
    # some response showing the number of RT/FAVS
    return render_template('prediction/aftermath.html', RT=RT_mean, FAV=FAV_mean, text=text, RTaa=RT_text, 
                           FAVaa=FAV_text,rt_bool=rt_bool, fv_bool=fv_bool, has = has,nohas = no_has)



@app.route('/evolution')
@login_required
def historic():

    df = pd.DataFrame()
    df = get_10tweets(current_user.username,dash = True)
    
    #maximum rt
    m_val = df['retweet_count'].max()
    #maximum fav
    m_val2 = df['favorite_count'].max()
    #some slices
    df_m = df.loc[df['retweet_count'] == m_val]
    df_m2 = df.loc[df['favorite_count'] == m_val2]
    #the means
    mean_rt = df['retweet_count'].mean()
    mean_fav = df['favorite_count'].mean()
    #the text of the maxs
    text_rt = df_m['text'].any()
    text_fav = df_m2['text'].any()
    
    #here we need to do the graph also
    #get_plot_images(current_user.username)
    
    return render_template('dashboard/trial.html',max_rt = m_val,max_fav = m_val2, mean_rt = mean_rt,
                           mean_fav = mean_fav, text_rt = text_rt, text_fav = text_fav)

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
