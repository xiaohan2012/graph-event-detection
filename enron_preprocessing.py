import pandas as pd

top_k_user = 10
top_k_msg = 10
df = pd.io.json.read_json('data/enron/interactions.json')
for sender in df['sender_id'].value_counts().index[:top_k_user]:
    print('sender: ', sender)
    print('msg:')
    print(df[df['sender_id'] == sender]['body'][:top_k_msg])
    print('-------------------------' * 2)

###################
# Some remove sender 256
###################
