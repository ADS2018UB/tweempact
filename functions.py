import pandas as pd
import numpy as np
import tweepy
import time
import os

def get_10tweets(username, n_tweets = 10, dash = False):
      
    #Authentication
    auth = tweepy.OAuthHandler(os.environ['consumer_key'], os.environ['consumer_secret'])
    auth.set_access_token(os.environ['access_key'],os.environ['access_secret'])
    api = tweepy.API(auth)

    tweets_10 = []
    MAX_ID = 9000000000000000000
    aux = 0
    
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
                MAX_ID = doc['id]
            
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