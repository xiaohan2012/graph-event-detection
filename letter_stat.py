import pandas as pd
import networkx as nx

df = pd.read_pickle('data/letter/interactions.pkl')

g = nx.DiGraph()
target_senders = []
for s in df['sender_id'].unique():
    rs = df[df['sender_id'] == s]['recipient_ids'].apply(lambda r: r[0]).unique()
    for r in rs:
        g.add_edge(s, r)
    if len(rs) > 1:
        target_senders.append(s)
        print("sender: {}".format(s))
        print("recipients: {}".format(' '.join(rs.tolist())))

out_degrees = g.out_degree(g.nodes())
print('Out of {} senders'.format(g.number_of_nodes()))
print('There are {} senders with multiple recipients'.format(
        len(filter(lambda v: v>1, out_degrees.values()))
        )
      )

senders_with_reply = []
for n1, n2 in g.edges_iter():
    if g.has_edge(n2, n1):
        senders_with_reply.append(n1)

print('There are {} senders with replies'.format(
        len(senders_with_reply))
      )
