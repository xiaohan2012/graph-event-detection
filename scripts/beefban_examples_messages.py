# coding: utf-8
import pandas as pd
import ujson as json

d = json.load(open('/cs/home/hxiao/public_html/event_html/data/beefban/event/meta_graph/result-greedy--U=15.0--dijkstra=False--timespan=1days----distance_weights={\"topics\":0.4,\"hashtag_bow\":0.4,\"bow\":0.2}--preprune_secs=1days----cand_tree_percent=0.00193485972267--root_sampling=adaptive.json'))
ms = map(lambda r: r['body'], d[0]['nodes'])
clean_msg = lambda t: t.replace('&amp;', '').replace('#beefban', '').replace('rt : ', '')
support = [clean_msg(ms[i]) for i in [1, 8, 9, 10, 12]]

ms = map(lambda r: r['body'], d[1]['nodes'])
oppose = [clean_msg(ms[i]) for i in [0, 1, 2, -1, 12]]

df = pd.DataFrame(
    {'support(event-1)': support, 'against(event-2)': oppose},
    columns=['support(event-1)', 'against(event-2)']
)
pd.set_option('display.max_colwidth', 60)
df.to_latex('tmp/beefban/example_tweets.tex', encoding='utf8')
