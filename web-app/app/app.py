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
from app.models import User
from app.forms import PredictionForm,LoginForm
import tweepy
from app.functions import get_10tweets
import plotly.graph_objs as go
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
#from werkzeug.wsgi import DispatcherMiddleware

#This is the web main page 
app = Flask(__name__)
dash1 = dash.Dash(__name__, server=app, url_base_pathname='/dash')

dash1.css.append_css({"external_url": "/static/css/dash.css"})

df = pd.DataFrame()
   
df = get_10tweets('ramonmir94', dash=True)

indicators = ['RT','FAV']
m_val = df['retweet_count'].max()
m_val2 =df['favorite_count'].max() 
df_m = df.loc[df['retweet_count']==m_val]
df_m2 = df.loc[df['favorite_count']==m_val2]
mean_rt = df['retweet_count'].mean()
mean_fav = df['favorite_count'].mean()
 
dash1.layout = html.Div([
    html.Div([

        html.Div([
            dcc.Dropdown(
                id='yaxis-column',
                options=[{'label': i, 'value': i} for i in indicators],
                value='RT'
            ),
        ],style={'width': '48%', 'display': 'inline-block'})
    ]),

    dcc.Graph(id='indicator-graphic'),

    dcc.RadioItems(
    id = 'show_more',
    options=[
        {'label': 'Show more', 'value': '1'},
        {'label': 'Hide', 'value': '0'},
        
    ],
    value= '0'
    ),
            
    html.Div(id = 'texts'),
    
    html.A("Home page", href='/', target="_blank")
])

@dash1.callback(
    dash.dependencies.Output('texts', 'children'),
    [dash.dependencies.Input('show_more','value')]
    )
def render_texts(dropdown_value):
    if(dropdown_value == '1'):
                   
        return html.Div([
                    html.Div([
                        html.P('Your maximum number of RT is {}.'.format(m_val)),
                        ],style={'width':'20%' ,'display':'inline-block'}),
                    html.Div([
                        html.P('Your maximum number of FAV is {}.'.format(m_val2)),
                        ],style={'width':'25%' ,'display':'inline-block'}),
                    html.Div([
                        html.P('Your RT mean is {}.'.format(mean_rt)),
                        ],style={'width':'30%' ,'display':'inline-block'}),
                    html.Div([
                        html.P('Your FAV mean is {}.'.format(mean_fav)),
                        ],style={'width':'20%' ,'display':'inline-block'}), 
                html.Br(),
                
                html.Div([
                    html.P('Your most retweeted tweet'),
                    dcc.Textarea(
                        id = 'maxr',
                        #title ='Tweet with maximum RT',
                        value= df_m['text'].any(),
                        disabled = True,
                        style={'width': '75%'}) 
                ],style={'width': '48%', 'display': 'inline-block'}),
                
                html.Div([
                    html.P('Your most favored tweet'),
                    dcc.Textarea(
                        id = 'maxf',
                        #title ='Tweet with maximum RT',
                        value= df_m2['text'].any(),
                        disabled = True,
                        style={'width': '75%'}) 
                    ],style={'width': '48%', 'float': 'right', 'display': 'inline-block'})
                ])
                    
    else:
        return 
 
@dash1.callback(
    dash.dependencies.Output('indicator-graphic', 'figure'),
    [dash.dependencies.Input('yaxis-column', 'value'),
     ])

def update_graph(yaxis_column_name
                 ):
    #df['TIME'] the date
    #df[yaxis-column]
    if(yaxis_column_name=='FAV'):
        val = df["favorite_count"]
    else:
        val = df["retweet_count"]
    return {
        'data': [go.Scatter(
            x=df.index ,#['created_at'],
            y = val,
            text = df['created_at'],
            mode='lines',

            
        )],
        'layout': go.Layout(
            xaxis={
                'title': 'Last 10 tweets',
                 
            },
            yaxis={
                'title': yaxis_column_name,
                 
            },
            margin={'l': 40, 'b': 40, 't': 10, 'r': 0},
            hovermode='closest'
        )
    }
#app.config['MONGO_DBNAME'] = 'foodb'
#app.config['MONGO_URI'] = 'mongodb://localhost:27017/foodb'
#mongo = PyMongo(app)

#application = DispatcherMiddleware(app, {'/dash': dash1.server})


@app.route('/')
def index():
 
  return redirect(url_for('login'))

if __name__ == '__main__':
    app.run()
       

@app.route('/faqs',methods = ['GET','POST'])
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

    if(RT_mean > RT_mean):
        RT_text = 'prediction over average'
    else:
        RT_text = 'prediction under average'
    if(FAV_mean > FAV_mean):
        FAV_text = 'prediction over average'
    else:
        FAV_text = 'prediction under average'   

    #text = request.args.get('text') 
    #some response showing the number of RT/FAVS
    return render_template('prediction/aftermath.html',RT = RT_mean, FAV = FAV_mean,text=text, RTaa = RT_text, FAVaa = FAV_text)


@app.route('/evolution')
@login_required
def historic():
    global df,m_val,m_val2,df_m,df_m2,mean_rt,mean_fav
    df = get_10tweets(current_user.username, dash=True)
    m_val = df['retweet_count'].max()
    m_val2 =df['favorite_count'].max() 
    df_m = df.loc[df['retweet_count']==m_val]
    df_m2 = df.loc[df['favorite_count']==m_val2]
    mean_rt = df['retweet_count'].mean()
    mean_fav = df['favorite_count'].mean()
    
    return redirect('/dash') 

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
