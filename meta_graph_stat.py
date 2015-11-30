import numpy as np
from pprint import pformat
from collections import Counter

from enron_graph import EnronUtil


class MetaGraphStat(object):
    def __init__(self, g, kws={}):
        self.g = g
        if len(g.nodes()) == 0 or len(g.edges()) == 0:
            raise ValueError("Empty graph(#nodes={}, #edges={}. Root {})".format(
                len(g.nodes()), len(g.edges()),
                g.nodes()[0]
            ))
            
        self.kws = {
            m: {}
            for m in dir(self)
            if (not m.startswith('_')
                and m != 'summary'
                and callable(getattr(self, m)))
        }
        if kws:
            self.kws.update(kws)

    def time_span(self):
        if len(self.g.nodes()) == 0:
            return {'start_time': None,
                    'end_time': None}
        else:
            ds = [self.g.node[i]['datetime']
                  for i in self.g.nodes()
                  if 'datetime' in self.g.node[i]]
            return {'start_time': min(ds),
                    'end_time': max(ds)}
            
    def temporal_traffic(self, time_resolution='day'):
        time_fields = ('year', 'month', 'day', 'hour', 'minute', 'second')
        assert time_resolution in time_fields

        selected_attrs = time_fields[0: time_fields.index(time_resolution) + 1]
        slice_datetime = (lambda dt: tuple([getattr(dt, attr)
                                            for attr in selected_attrs]))
        time_signatures = [slice_datetime(self.g.node[n]['datetime'])
                           for n in self.g.nodes()]
        return {'email_count_hist': sorted(Counter(time_signatures).items())}
        
    def edge_costs(self, max_values=[1.0]):
        costs = np.asarray([self.g[s][t]['c'] for s, t in self.g.edges()])
        data = {'histogram(all)': np.histogram(costs)}
        for max_value in max_values:
            key = 'histogram(<={})'.format(max_value)
            data[key] = np.histogram(costs[costs <= max_value])
        return data

    def basic_structure_stats(self):
        in_degrees = np.asarray([self.g.in_degree(n)
                                 for n in self.g.nodes()],
                                dtype=np.int64)
        out_degrees = np.asarray([self.g.out_degree(n)
                                  for n in self.g.nodes()],
                                 dtype=np.int64)
        degrees = in_degrees + out_degrees

        return {
            '#nodes': len(self.g.nodes()),
            '#singleton': len(np.nonzero(degrees == 0)[0]),
            '#edges': len(self.g.edges()),
            'in_degree': {
                'min': in_degrees.min() if in_degrees.size else None,
                'max': in_degrees.max() if in_degrees.size else None,
                'average': in_degrees.mean(),
                'median': np.median(in_degrees)
            },
            'out_degree': {
                'min': out_degrees.min() if len(in_degrees) > 0 else None,
                'max': out_degrees.max() if len(in_degrees) > 0 else None,
                'average': out_degrees.mean(),
                'median': np.median(out_degrees)
            }
        }

    def topics(self, id2msg, dictionary, lda, top_k=10):
        message_ids = [self.g.node[n]['message_id']
                       for n in self.g.nodes()]
        concated_msg = ' '.join([id2msg[mid] for mid in message_ids])
        bow = dictionary.doc2bow(EnronUtil.tokenize_document(concated_msg))
        topic_dist = lda.get_document_topics(
            bow,
            minimum_probability=0
        )
        topic_dist = np.asarray([v for _, v in topic_dist])
        
        beta = lda.state.get_lambda()

        # normalize and weight by beta dist
        weighted_terms = (
            beta / beta.sum(axis=1)[:, None] * topic_dist[:, None]
        ).sum(axis=0)

        print(weighted_terms)
        bestn = np.argsort(weighted_terms)[::-1][:top_k]
        print(bestn)
        topic_terms = [lda.id2word[id] for id in bestn]

        return {'topic_dist': topic_dist,
                'topic_terms': topic_terms}

    def summary(self):
        return pformat(
            {m: getattr(self, m)(**self.kws[m])
             for m in dir(self)
             if not m.startswith('_') and m != 'summary' and callable(getattr(self, m))})
        
