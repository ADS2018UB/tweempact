def balanced(df):
	import datetime,time
	import numpy as numpy
	import pandas as pd
	
	cleaned = df[["id", "created_at","entities", "extended_entities","favorite_count","retweet_count","source","text", "truncated","user","quoted_status_id"]]
	ids = [user["id"] for user in cleaned["user"]]
	cleaned["id_num"] = ids

	for _id in ids:
		subset = cleaned[cleaned["id_num"]==_id]
		subset = subset.reset_index(drop=True)
		reindexed = subset["created_at"]
		reindexed = subset["created_at"].reset_index(drop=True)
		#convert tweet date into python date
		subset["created_at_pydate"] = [time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(reindexed[i],'%a %b %d %H:%M:%S +0000 %Y'))for i in range(0,len(reindexed))]
		subset = subset.sort_values(by="created_at_pydate")
		last10_tweets = subset[:-1][-10:]
		RT_l10 = np.mean(last10_tweets["retweet_count"])
		FC_l10 = np.mean(last10_tweets["favorite_count"])
		tw = subset[-1:]
	return tw
