def text_dataset(df):
    import re
    import pandas as pd
    l = list(df["text"])
    filtr = ["RT" not in i for i in l]
    df = df[filtr].reset_index(drop=True)
    
    Tweet =[re.sub("[(\n)(\r)]"," ",tweet) for tweet in df["text"]]
    entities = [tweet for tweet in df["entities"]]
    FC = [tweet for tweet in df["favorite_count"]]
    RT = [tweet for tweet in df["retweet_count"]]
    id_ = [tweet for tweet in df["id"]]
    
    CA = df["created_at"]
    CA_l = [time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(CA[i],'%a %b %d %H:%M:%S +0000 %Y'))for i in range(0,len(CA))]
    
    output = pd.DataFrame([id_,Tweet,CA_l,entities,FC,RT]).T
    output.reset_index(drop=True)
    output.columns = ["id", "Tweet", "created_at", "entities", "FC", "RT"]
    return output