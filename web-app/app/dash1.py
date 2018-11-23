
#import dash
#from app.app import app  

#app = dash.Dash(name='app1', sharing=True, server= app, url_base_pathname='/app1')

import dash
import dash_core_components as dcc
import dash_html_components as html
from app.functions import get_10tweets #aixo es per probar-ho ara
import pandas as pd
import plotly.graph_objs as go
from flask_login import current_user

dash1 = dash.Dash()

df = pd.DataFrame()
df = get_10tweets(current_user.username, dash=True)

indicators = ['RT','FAV']
m_val = df['retweet_count'].max()
m_val2 =df['favorite_count'].max() 
df_m = df[df['retweet_count']==m_val]
df_m2 = df[df['favorite_count']==m_val2]
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
    
@dash1.callback(
    dash.dependencies.Output('output-choose', 'children'),
    [dash.dependencies.Input('choose', 'value')])
def callback_a(dropdown_value):
    return 'The value is "{}"'.format(dropdown_value)
    
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