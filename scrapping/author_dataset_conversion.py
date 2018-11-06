 def author_dataset_conversion(df):   
    import time
    import numpy as np
    import pandas as pd

    cleaned = df[["id", "created_at","entities", "extended_entities","favorite_count","retweet_count","source","text", "truncated","user","quoted_status_id"]]
    ids = [user["id"] for user in cleaned["user"]]
    cleaned["id_num"] = ids

    #preparing output variables
    output = pd.DataFrame()
    users = []
    mean_RT_last10,mean_FC_last10 = [],[]
    sd_RT,sd_FC  = [],[]
    y1,y2=[],[]

    for _id in np.unique(ids):
        subset = cleaned[cleaned["id_num"]==_id].reset_index(drop=True)

        #filtering tweets from all tweets and RT
        l = list(subset["text"])
        filtr = ["RT" not in i for i in l]
        subset = subset[pd.Series(filtr)]
        if len(subset)>=11:
            reindexed = subset["created_at"].reset_index(drop=True)
            #convert tweet date into python date
            subset["created_at_pydate"] = [time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(reindexed[i],'%a %b %d %H:%M:%S +0000 %Y'))for i in range(0,len(reindexed))]
            subset = subset.sort_values(by="created_at_pydate").reset_index(drop=True)

            last10_tweets = subset[-11:-1]
            last_tweet = subset[-1:]
            #RT parameters last 10 tweets
            mean_RT_last10.append(np.mean(last10_tweets["retweet_count"]))
            sd_RT.append(np.std(last10_tweets["retweet_count"]))
            #FC parameters last 10 tweets
            mean_FC_last10.append(np.mean(last10_tweets["favorite_count"]))
            sd_FC.append(np.std(last10_tweets["favorite_count"]))
            #take json user
            j_user = subset[-1:]["user"].reset_index(drop=True)[0]
            users.append(j_user)
            #parameters of last tweet
            y1.append(np.mean(last_tweet["favorite_count"]))
            y2.append(np.mean(last_tweet["retweet_count"]))
    output["j_user"]=users
    output["RT_l10"]=mean_RT_last10
    output["sd_RT"]=sd_RT
    output["FC_l10"]=mean_FC_last10
    output["sd_FC"]=sd_FC
    output["FC"]=y1
    output["RT"]=y2
    return output