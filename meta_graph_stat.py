import scipy
import numpy as np
import networkx as nx
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
            
        for kw in kws:
            assert hasattr(self, kw) and callable(getattr(self, kw))
        self.kws = kws

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

    def email_content(self, interactions, top_k=5, unique=True):
        id2subject = {}
        for m in interactions:
            id2subject[m['message_id']] = m['subject']
        msgs = []
        mids = [self.g.node[n]['message_id']
                for n in nx.topological_sort(self.g)]

        if unique:
            msgs = set()
            for mid in mids:
                cand_msg = id2subject[mid]
                if cand_msg not in msgs:
                    msgs.add(cand_msg)
                if len(msgs) == top_k:
                    break
            msgs = list(msgs)
        else:
            msgs = [id2subject[id] for id in mids[:top_k]]
        return {
            'subjects(top{})'.format(top_k): msgs
        }
        
    def _topic_divergence(self, msg_ids, id2msg, dictionary, lda):
        raw_topics = [
            lda.get_document_topics(
                dictionary.doc2bow(
                    EnronUtil.tokenize_document(id2msg[id_])
                )
            )
            for id_ in msg_ids
        ]
        topic_vects = np.array([[v for _, v in topics]
                                for topics in raw_topics])
        mean_topic_vect = np.mean(topic_vects, axis=0)
        diffs = [scipy.stats.entropy(mean_topic_vect, v)
                 for v in topic_vects]

        return np.mean(diffs)

    def topics(self, interactions, dictionary, lda, top_k=10):
        id2msg = {}
        for m in interactions:
            id2msg[m['message_id']] = "{} {}".format(
                m['subject'], m['body']
            )

        # topic_dist
        message_ids = [self.g.node[n]['message_id']
                       for n in self.g.nodes()]
        concated_msg = ' '.join([id2msg[mid] for mid in message_ids])
        bow = dictionary.doc2bow(EnronUtil.tokenize_document(concated_msg))
        topic_dist = lda.get_document_topics(
            bow,
            minimum_probability=0
        )
        topic_dist = np.asarray([v for _, v in topic_dist])
        
        # topic_terms
        beta = lda.state.get_lambda()

        # normalize and weight by beta dist
        weighted_terms = (
            beta / beta.sum(axis=1)[:, None] * topic_dist[:, None]
        ).sum(axis=0)

        bestn = np.argsort(weighted_terms)[::-1][:top_k]

        topic_terms = [lda.id2word[id] for id in bestn]
        
        topic_divergence = self._topic_divergence(message_ids, id2msg,
                                                  dictionary, lda)
        return {'topic_dist': topic_dist,
                'topic_terms': topic_terms,
                'topic_divergence': topic_divergence}

    def participants(self, people_info, interactions, top_k=10):
        peopleid2info = {r['id']: (r['name'], r['email'])
                         for r in people_info}

        mid2sender = {m['message_id']: m['sender_id']
                      for m in interactions}
        mid2recipients = {m['message_id']: m['recipient_ids']
                          for m in interactions}
        
        def populate_user_info(counter):
            data = dict(map(lambda (people_id, count):
                            (peopleid2info[people_id], count),
                            counter.items()))
            return Counter(data)

        result = {}
        result['sender_count'] = Counter(
            [mid2sender[self.g.node[n]['message_id']]
             for n in self.g.nodes()]
        )

        result['sender_count'] = populate_user_info(result['sender_count'])

        result['recipient_count'] = Counter([
            r
            for n in self.g.nodes()
            for r in mid2recipients[self.g.node[n]['message_id']]
        ])
        result['recipient_count'] = populate_user_info(
            result['recipient_count']
        )
        
        result['participant_count'] = (result['sender_count'] +
                                       result['recipient_count'])

        result['sender_entropy'] = scipy.stats.entropy(
            result['sender_count'].values())
        result['recipient_entropy'] = scipy.stats.entropy(
            result['recipient_count'].values())
        result['participant_entropy'] = scipy.stats.entropy(
            result['participant_count'].values())
        
        for key in ('sender_count', 'recipient_count', 'participant_count'):
            result[key] = sorted(result[key].items(),
                                 key=lambda (info, c): (c, info),
                                 reverse=True)[:top_k]
        
        return result

    def summary(self):
        return pformat(
            {m: getattr(self, m)(**self.kws.get(m, {}))
             for m in dir(self)
             if (not m.startswith('_') and
                 m != 'summary' and
                 callable(getattr(self, m)) and
                 self.kws.get(m) is not False  # if False, disable
             )}
        )
        
