
#import dash
#from app.app import app  

#app = dash.Dash(name='app1', sharing=True, server= app, url_base_pathname='/app1')

import dash
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import tweepy
import time
import pandas as pd
import plotly.graph_objs as go

def get_10tweets(username, n_tweets = 10, dash = False):
    
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

    tweets_10 = []
    count = 10
    
    while len(tweets_10) < 10:
        
        try:
            tweets = api.user_timeline(screen_name=username, count=count)
        except tweepy.TweepError:
            return 0, tweets_10
        
        for tweet in tweets:
            doc = tweet._json
            doc['id'] = str(doc['id'])
            
            if doc not in tweets_10 and not doc['text'].startswith('RT '):
                tweets_10.append(doc)
            else:
                count += 1
            
            if len(tweets_10) == 10:
                break

    out = pd.DataFrame()
    t = pd.DataFrame(tweets_10)
    
    if dash == False:
        mean_FC_last10, sd_FC = np.mean(t["favorite_count"]), np.std(t["favorite_count"])
        mean_RT_last10, sd_RT = np.mean(t["retweet_count"]), np.std(t["retweet_count"])

        out["j_user"]=t["user"][-1:]
        out["RT_l10"]=mean_RT_last10
        out["sd_RT"]=sd_RT
        out["FC_l10"]=mean_FC_last10
        out["sd_FC"]=sd_FC
        out = out.reset_index(drop=True)  
        return out
    
    if dash:
        t1 = t[["text", "favorite_count", "retweet_count"]]
        CA = t["created_at"]
        CA_l = [time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(CA[i],'%a %b %d %H:%M:%S +0000 %Y'))for i in range(0,len(CA))]
        t1["created_at"] = CA_l
        return t1
    
app = dash.Dash()

df = pd.DataFrame()
df = get_10tweets('ramonmir94', dash=True)

indicators = ['RT','FAV']
m_val = df['retweet_count'].max()
m_val2 =df['favorite_count'].max() 
df_m = df[df['retweet_count']==m_val]
df_m2 = df[df['favorite_count']==m_val2]
mean_rt = df['retweet_count'].mean()
mean_fav = df['favorite_count'].mean()
 
app.layout = html.Div([
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
    
    #dcc.Input(
    #'Maximum RT value',
    #readonly = False,
    #type = 'number',
    #value= m_val
    #),
    dcc.RadioItems(
    id = 'choose',
    options=[
        {'label': 'Maximum RT', 'value': m_val},
        {'label': 'Maximum FAV', 'value': m_val2},
        {'label': 'Mean RT', 'value': mean_rt},
        {'label': 'Mean FAV', 'value': mean_fav}
    ],
    value= m_val
    ),
    html.Div(id='output-choose'),
    
    html.Div([ 
        html.Div([
            html.P('Your most retweeted tweet'),
            dcc.Textarea(
                #id = 'max',
                #title ='Tweet with maximum RT',
                value= df_m['text'].any(),
                disabled = True,
                style={'width': '75%'}) 
            ],style={'width': '48%', 'display': 'inline-block'}),
            
            
        html.Div([
            html.P('Your most favored tweet'),
            dcc.Textarea(
                #id = 'max',
                #title ='Tweet with maximum RT',
                value= df_m2['text'].any(),
                disabled = True,
                style={'width': '75%'}
                ) 
            ],style={'width': '48%', 'float': 'right', 'display': 'inline-block'})
            
        ]),
    html.A("Home page", href='/', target="_blank")
])
    
@app.callback(
    dash.dependencies.Output('output-choose', 'children'),
    [dash.dependencies.Input('choose', 'value')])
def callback_a(dropdown_value):
    return 'The value is "{}"'.format(dropdown_value)
    
@app.callback(
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

if __name__ == '__main__':
    app.run_server()