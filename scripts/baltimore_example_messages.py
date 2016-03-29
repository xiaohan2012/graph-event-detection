# coding: utf-8
import pandas as pd
import ujson as json

d = json.load(open('/cs/home/hxiao/public_html/event_html/data/baltimore/event/meta_graph/result-greedy--U=15.0--dijkstra=False--timespan=1days----distance_weights={\"topics\":0.4,\"hashtag_bow\":0.4,\"bow\":0.2}--preprune_secs=1days--self_talking_penalty=0.0----cand_tree_percent=0.01--root_sampling=adaptive.json'))
clean_msg = lambda t: t.replace('&amp;', '').replace('rt : ', '')

ms = map(lambda r: r['body'], d[0]['nodes'])

anger = [clean_msg(ms[i]) for i in [0, 1, 3, 6, 7]]

ms = map(lambda r: r['body'], d[2]['nodes'])
report = [clean_msg(ms[i]) for i in [0, 1, 2, 4, 5]]

df = pd.DataFrame(
    {'descriptive(event-3)': report, 'emotional(event-1)': anger},
    columns=['emotional(event-1)', 'descriptive(event-3)']
)
pd.set_option('display.max_colwidth', 50)
df.to_latex('tmp/baltimore/example_tweets.tex', encoding='utf8')
