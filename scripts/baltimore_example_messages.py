# coding: utf-8
import pandas as pd
import ujson as json

d = json.load(open('/cs/home/hxiao/public_html/event_html/data/baltimore/event/meta_graph/result-greedy--U=15.0--dijkstra=False--timespan=1days----distance_weights={\"topics\":0.4,\"hashtag_bow\":0.4,\"bow\":0.2}--preprune_secs=1days--self_talking_penalty=0.0----cand_tree_percent=0.01--root_sampling=adaptive.json'))
ms = map(lambda r: r['body'], d[0]['nodes'])
anger = [ms[0], ms[1], ms[3], ms[6], ms[7]]

ms = map(lambda r: r['body'], d[2]['nodes'])
report = [ms[0], ms[1], ms[2], ms[4], ms[5]]

df = pd.DataFrame(
    {'descriptive(event-3)': report, 'emotional(event-1)': anger},
    columns=['emotional(event-1)', 'descriptive(event-3)']
)
pd.set_option('display.max_colwidth', 60)
df.to_latex('tmp/baltimore/example_tweets.tex', encoding='utf8')
