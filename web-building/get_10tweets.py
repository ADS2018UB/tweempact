def get_10tweets(username):
    import pandas as pd
    import numpy as np
    
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
    return out