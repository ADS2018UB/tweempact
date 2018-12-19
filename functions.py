import pandas as pd
import numpy as np
import tweepy
import time
import os
import matplotlib.dates as mdates
import datetime
import matplotlib.pyplot as plt

from sklearn.externals import joblib


def get_TT():
    TT = []
    auth = tweepy.OAuthHandler(os.environ['consumer_key'], os.environ['consumer_secret'])
    auth.set_access_token(os.environ['access_key'],os.environ['access_secret'])
    api = tweepy.API(auth)
    results = api.trends_place(23424950)
    for location in results:
        for trend in location["trends"]:
            TT.append(trend["name"])
    return TT


def get_10tweets(username, n_tweets = 10, dash = False):
      
    #Authentication
    auth = tweepy.OAuthHandler(os.environ['consumer_key'], os.environ['consumer_secret'])
    auth.set_access_token(os.environ['access_key'],os.environ['access_secret'])
    api = tweepy.API(auth)

    tweets_10 = []
    MAX_ID = 9000000000000000000
    aux = 0
    count = 10
    while len(tweets_10) < n_tweets:
        
        try:
            tweets = api.user_timeline(screen_name=username, count=count, max_id = MAX_ID)
        except tweepy.TweepError:
            return 0, tweets_10
        
        for tweet in tweets:
            doc = tweet._json
            doc['id'] = str(doc['id'])
            
            if doc not in tweets_10 and not doc['text'].startswith('RT '):
                tweets_10.append(doc)
            else:
                MAX_ID = doc['id']
            
            if len(tweets_10) == n_tweets:
                break
        if aux > 20:
            # Could only find less than n_tweets tweets in n_tweets*20 searched tweets.
            return 2, tweets_10
        aux += 1

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
    
def get_plot_images(username):
    
    out = get_10tweets(username, 10, True) # funció de l'Albert
    data = out["created_at"]
    FC = out['favorite_count']
    RT = out['retweet_count']
    data = [datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S') for date in data]
    FC = [int(fc) for fc in FC]
    RT = [int(rt) for rt in RT]
    
    plt.figure(figsize=(10,7))
    plt.plot(data, FC, color=(232/255,28/255,79/255), linewidth=3)
    plt.plot(data, FC, "ok")
    cur_axes = plt.gca()
    cur_axes.xaxis.set_major_formatter(mdates.DateFormatter("%d-%b"))
    plt.ylabel('Favorite Count')
    plt.savefig('static/images/FCplot.png', transparent=True)
    
    plt.figure(figsize=(10,7))
    plt.plot(data, RT, color=(25/255, 207/255, 134/255), linewidth=3)
    plt.plot(data, RT, "ok")
    cur_axes = plt.gca()
    cur_axes.xaxis.set_major_formatter(mdates.DateFormatter("%d-%b"))
    cur_axes.set_facecolor("w")
    plt.ylabel('Retweet count')
    plt.savefig('static/images/RTplot.png')
    return

def load_model(filename):
    return joblib.load("models/"+filename)

class segmenta():
    
    def __init__(self):
        self.intervals = {}
    
    def transform(self,y):
        k, z = 0, 0
        for a, b in [[20,5],
                     [50,10],
                     [100,25],
                     [1000,100],
                     [10000,1000],
                     [50000,10000]]: 
            for i in np.arange(z,a,b):
                self.intervals[k] = [i,i+b-1]
                k+=1
            z = a
        self.intervals[k] = [50000,99999999]

        for j in self.intervals:
            c = self.intervals[j]
            if (y>=c[0]) & (y<=c[1]):
                C = j

        return C

def prepare_prediction(username, text):
    cols = ['Tweet','RT_l10','sd_RT','FC_l10','sd_FC','friends_count','followers_count']
    file = pd.DataFrame(columns=cols)
    for col in cols:
        file[col]=np.zeros(1)
    
    out = get_10tweets(username, 10, False)
    j_user = out['j_user'][0]
    for col in cols[5:7]:
        file[col] = int(j_user[col])
    file['Tweet'] = text
    file['RT_l10'] = out['RT_l10'][0]
    file['sd_RT'] = out['sd_RT'][0]
    file['FC_l10'] = out['FC_l10'][0]
    file['sd_FC'] = out['sd_FC'][0]
    
    return file

def predict(df):
    # predict user type:
    df_author = df[['RT_l10', 'sd_RT', 'FC_l10', 'sd_FC', 'friends_count', 'followers_count']]
    FC_class  = load_model('trained_FC_class.sav').predict(df_author)
    RT_class  = load_model('trained_RT_class.sav').predict(df_author)
    
    df_tweet = df['Tweet']

    ### FC
    mu_FC = df['FC_l10']
    sd_FC = df['sd_FC']

    seg = segmenta()
    k = seg.transform(int(mu_FC))

    if FC_class==0:
        FC = seg.intervals[k]

    elif FC_class==1: 
        X  = load_model('trained_vect_FC_C1.sav').transform(df_tweet).todense()
        FC = seg.intervals[int(0.4*load_model('trained_FC_C1_tweet.sav').predict(X)[0] + 0.6*k)]

    elif FC_class==2: 
        X  = load_model('trained_vect_FC_C2.sav').transform(df_tweet).todense()
        FC = seg.intervals[int(0.2*load_model('trained_FC_C2_tweet.sav').predict(X)[0] + 0.8*k)]
    
    ### RT
    mu_RT = df['RT_l10']
    sd_RT = df['sd_RT']

    seg = segmenta()
    k = seg.transform(int(mu_RT))

    if RT_class==0:
        RT = seg.intervals[k]

    elif RT_class==1: 
        X  = load_model('trained_vect_RT_C1.sav').transform(df_tweet).todense()
        RT = seg.intervals[int(0.4*load_model('trained_RT_C1_tweet.sav').predict(X)[0] + 0.6*k)]

    elif RT_class==2: 
        X  = load_model('trained_vect_RT_C2.sav').transform(df_tweet).todense()
        RT = seg.intervals[int(0.2*load_model('trained_RT_C2_tweet.sav').predict(X)[0] + 0.8*k)]
        
    # apaño chapuzero a manija
    #RT = int((RT[0]+RT[1])/2 + random.random()*sd_RT[0])
    #FC = int((FC[0]+FC[1])/2 + random.random()*sd_FC[0])
            
    return FC, RT