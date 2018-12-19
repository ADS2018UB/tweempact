# -*- coding: utf-8 -*-
"""
Created on Wed Oct 31 17:47:45 2018

@author: PC
"""
from flask import Flask, make_response, request
from flask_pymongo import PyMongo
from flask import abort, jsonify, redirect, render_template
from flask import url_for
from flask_login import LoginManager, current_user
from flask_login import login_user, logout_user
from flask_login import login_required
from app.models import User
from app.forms import PredictionForm, LoginForm
import tweepy
from app.functions import *
import plotly.graph_objs as go
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
import time

# Classifiers importation
from sklearn.metrics import recall_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC, LinearSVC, NuSVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier, GradientBoostingClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis
from sklearn import neural_network
from sklearn.naive_bayes import BernoulliNB

# Others
import seaborn as sns
from sklearn import linear_model, metrics, model_selection
from sklearn.preprocessing import StandardScaler
from sklearn.externals import joblib

# from werkzeug.wsgi import DispatcherMiddleware

# This is the web main page
app = Flask(__name__)

dash1 = dash.Dash(__name__, server=app, url_base_pathname='/dash')

dash1.css.append_css({"external_url": "/static/css/dash.css"})
dash1.css.append_css({"external_url": "/static/css/homepage.css"})
dash1.scripts.append_script({'external_url': '/static/js/insert_header.js'})

#df = pd.DataFrame()

df = get_10tweets('ramonmir94', dash=True)

indicators = ['RT', 'FAV']
m_val = df['retweet_count'].max()
m_val2 = df['favorite_count'].max()
df_m = df.loc[df['retweet_count'] == m_val]
df_m2 = df.loc[df['favorite_count'] == m_val2]
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
        ], style={'width': '48%', 'display': 'inline-block'})
    ]),

    dcc.Graph(id='indicator-graphic'),

    dcc.RadioItems(
        id='show_more',
        options=[
            {'label': 'Show more', 'value': '1'},
            {'label': 'Hide', 'value': '0'},

        ],
        value='0'
    ),

    html.Div(id='texts'),

    html.A("Home page", href='/', target="_blank")
])


@dash1.callback(
    dash.dependencies.Output('texts', 'children'),
    [dash.dependencies.Input('show_more', 'value')]
)
def render_texts(dropdown_value):
    if dropdown_value == '1':

        return html.Div([
            html.Div([
                html.P('Your maximum number of RT is {}.'.format(m_val)),
            ], style={'width': '20%', 'display': 'inline-block'}),
            html.Div([
                html.P('Your maximum number of FAV is {}.'.format(m_val2)),
            ], style={'width': '25%', 'display': 'inline-block'}),
            html.Div([
                html.P('Your RT mean is {}.'.format(mean_rt)),
            ], style={'width': '30%', 'display': 'inline-block'}),
            html.Div([
                html.P('Your FAV mean is {}.'.format(mean_fav)),
            ], style={'width': '20%', 'display': 'inline-block'}),
            html.Br(),

            html.Div([
                html.P('Your most retweeted tweet'),
                dcc.Textarea(
                    id='maxr',
                    # title ='Tweet with maximum RT',
                    value=df_m['text'].any(),
                    disabled=True,
                    style={'width': '75%'})
            ], style={'width': '48%', 'display': 'inline-block'}),

            html.Div([
                html.P('Your most favored tweet'),
                dcc.Textarea(
                    id='maxf',
                    # title ='Tweet with maximum RT',
                    value=df_m2['text'].any(),
                    disabled=True,
                    style={'width': '75%'})
            ], style={'width': '48%', 'float': 'right', 'display': 'inline-block'})
        ])

    else:
        return


@dash1.callback(
    dash.dependencies.Output('indicator-graphic', 'figure'),
    [dash.dependencies.Input('yaxis-column', 'value'),
     ])
def update_graph(yaxis_column_name):
    # df['TIME'] the date
    # df[yaxis-column]
    if yaxis_column_name == 'FAV':
        val = df["favorite_count"]
    else:
        val = df["retweet_count"]
    return {
        'data': [go.Scatter(
            x=df.index,  # ['created_at'],
            y=val,
            text=df['created_at'],
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


# app.config['MONGO_DBNAME'] = 'foodb'
# app.config['MONGO_URI'] = 'mongodb://localhost:27017/foodb'
# mongo = PyMongo(app)

# application = DispatcherMiddleware(app, {'/dash': dash1.server})


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
        # whatever we do with text etc
        text = form.text.data
        return redirect(url_for('prediction_made', text=text))
    TT_nohas = []
    for i in range(0,10):
        if("#" in Trending[i]):
           TT_nohas.append(Trending[i].strip('#'))
        else:
            TT_nohas.append(Trending[i])
    return render_template('prediction/submit.html', form=form, TT = Trending, TTno = TT_nohas)


@app.route('/prediction/aftermath/<text>', methods=['GET', 'POST'])
@login_required
def prediction_made(text):
    # It should be a button that send us back to prediction
    df = pd.DataFrame()
    df = get_10tweets(current_user.username)

    info_user = prepare_prediction(current_user.username, text)
    FC_pred, RT_pred = predict(info_user)

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

        # text = request.args.get('text')
    # some response showing the number of RT/FAVS
    return render_template('prediction/aftermath.html', RT=RT_mean, FAV=FAV_mean, text=text, RTaa=RT_text, FAVaa=FAV_text,
        rt_bool=rt_bool, fv_bool=fv_bool, FC_pred=FC_pred, RT_pred=RT_pred)

@app.route('/evolution')
@login_required
def historic():

    df = pd.DataFrame()
    df = get_10tweets(current_user.username,dash = True)
    get_plot_images(current_user.username)
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
    
    
    return render_template('dashboard/trial.html',max_rt = m_val,max_fav = m_val2, mean_rt = mean_rt,
                           mean_fav = mean_fav, text_rt = text_rt, text_fav = text_fav,trial = "RT")
    
#@app.route('/evolution')
#@login_required
#def historic():
 #   global df, m_val, m_val2, df_m, df_m2, mean_rt, mean_fav
  #  df = get_10tweets(current_user.username, dash=True)
  #  m_val = df['retweet_count'].max()
   # m_val2 = df['favorite_count'].max()
    #df_m = df.loc[df['retweet_count'] == m_val]
    #df_m2 = df.loc[df['favorite_count'] == m_val2]
    #mean_rt = df['retweet_count'].mean()
    #mean_fav = df['favorite_count'].mean()

    #return redirect('/dash')


app.config['SECRET_KEY'] = 'esydM2ANhdcoKwdVa0jWvEsbPFuQpMjg'  # Create your own.
app.config['SESSION_PROTECTION'] = 'strong'
app.config["CACHE_TYPE"] = "null"  
#cache.init_app(app)
login_manager = LoginManager()
login_manager.setup_app(app)
login_manager.login_view = 'login'


# @login_manager.user_loader
# def load_user(user_id):
# """Flask-Login hook to load a User instance from ID."""
# u = mongo.db.users.find_one({"username": user_id})
# if not u:
#   return None
# return User(u['username'])

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
        # password = form.password.data.lower().strip()
        # user = username
        with open('consumer_key.txt', 'r') as f:
            consumer_key = f.read()
        f.close()

        with open('consumer_secret.txt', 'r') as f:
            consumer_secret = f.read()
        f.close()

        with open('access_key.txt', 'r') as f:
            access_key = f.read()
        f.close()

        with open('access_secret.txt', 'r') as f:
            access_secret = f.read()
        f.close()

        # Authentication
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_key, access_secret)
        api = tweepy.API(auth)

        try:
            user = api.get_user(id=username)

        except tweepy.TweepError:
            user = False
        # We need to substitute this for a line that actually looks inside twitter
        # user = mongo.db.users.find_one({"username": form.username.data})

        if user:  # and User.validate_login(user['password'], form.password.data):
            user_obj = User(username)  # ['username'])
            login_user(user_obj)
            
            return redirect(url_for('prediction_submit'))
        else:
            error = 'Incorrect twitter username'  # or password.'
    return render_template('login.html',
                           form=form, error=error)


@app.route('/logout/')
def logout():
    logout_user()
    return redirect(url_for('login'))
