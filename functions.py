import pandas as pd
import numpy as np
import tweepy


def get_10tweets(username):
    
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
    
    mean_FC_last10, sd_FC = np.mean(t["favorite_count"]), np.std(t["favorite_count"])
    mean_RT_last10, sd_RT = np.mean(t["retweet_count"]), np.std(t["retweet_count"])
    
    out["j_user"]=t["user"][-1:]
    out["RT_l10"]=mean_RT_last10
    out["sd_RT"]=sd_RT
    out["FC_l10"]=mean_FC_last10
    out["sd_FC"]=sd_FC
    out = out.reset_index(drop=True)
    
    return out# -*- coding: utf-8 -*-

