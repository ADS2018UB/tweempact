import pandas as pd
import numpy as np
import tweepy
import time
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime
from sklearn.externals import joblib

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

def get_TT():
    
    TT = []
    
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
    results = api.trends_place(23424950)
    for location in results:
        for trend in location["trends"]:
            TT.append(trend["name"])
    return TT

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
            
            if doc not in tweets_10 and not doc['text'].startswith('RT ') and doc["in_reply_to_status_id"] is None:
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

def get_plot_images(username):
    
    out = get_10tweets(username, 10, True) # funció de l'Albert
    
    dates = out["created_at"]

    data = [datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S') for date in dates]
    out["dates"] = data
    data = sorted(data)

    out = out.sort_values(by="dates")

    FC = out['favorite_count']
    RT = out['retweet_count']

    FC = [int(fc) for fc in FC]
    RT = [int(rt) for rt in RT]
    
    plt.figure(figsize=(10,7))
    plt.plot(data, FC, color=(232/255,28/255,79/255), linewidth=3)
    plt.plot(data, FC, "ok")
    cur_axes = plt.gca()
    cur_axes.xaxis.set_major_formatter(mdates.DateFormatter("%d-%b"))
    plt.ylabel('Favorite Count')
    plt.savefig('app/static/images/FCplot.png', transparent=True)
    
    plt.figure(figsize=(10,7))
    plt.plot(data, RT, color=(25/255, 207/255, 134/255), linewidth=3)
    plt.plot(data, RT, "ok")
    cur_axes = plt.gca()
    cur_axes.xaxis.set_major_formatter(mdates.DateFormatter("%d-%b"))
    cur_axes.set_facecolor("w")
    plt.ylabel('Retweet count')
    plt.savefig('app/static/images/RTplot.png')
    return

def load_model(filename):
    return joblib.load("app/models/"+filename)

class segmenta():
    
    def __init__(self):
        self.intervals = {}
    
    def transform(self,y):
        k, z = 0, 0
        for a, b in [[15,5],
                     [25,10],
                     [50,25],
                     [100,50],
                     [1000,900],
                     [10000,4500],
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
        FC = seg.intervals[load_model('trained_FC_C1_tweet.sav').predict(X)[0]]
        if (np.mean(FC) > mu_FC + sd_FC*10)[0] or (np.mean(FC) < mu_FC - sd_FC*100)[0]:
            FC = seg.intervals[k]

    elif FC_class==2: 
        X  = load_model('trained_vect_FC_C2.sav').transform(df_tweet).todense()
        FC = seg.intervals[load_model('trained_FC_C2_tweet.sav').predict(X)[0]]
        if (np.mean(FC) > mu_FC + sd_FC*100)[0] or (np.mean(FC) < mu_FC - sd_FC*100)[0]:
            FC = seg.intervals[k]
            
    ### RT
    mu_RT = df['RT_l10']
    sd_RT = df['sd_RT']

    seg = segmenta()
    k = seg.transform(int(mu_RT))

    if RT_class==0:
        RT = seg.intervals[k]

    elif RT_class==1: 
        X  = load_model('trained_vect_RT_C1.sav').transform(df_tweet).todense()
        RT = seg.intervals[load_model('trained_RT_C1_tweet.sav').predict(X)[0]]
        if (np.mean(RT) > mu_RT + sd_RT*100)[0] or (np.mean(RT) < mu_RT - sd_RT*100)[0]:
            RT = seg.intervals[k]

    elif RT_class==2: 
        X  = load_model('trained_vect_RT_C2.sav').transform(df_tweet).todense()
        RT = seg.intervals[load_model('trained_RT_C2_tweet.sav').predict(X)[0]]
        if (np.mean(RT) > mu_RT + sd_RT*100)[0] or (np.mean(RT) < mu_RT - sd_RT*100)[0]:
            RT = seg.intervals[k]
            
    return FC, RT