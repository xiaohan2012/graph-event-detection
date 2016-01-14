import scipy
import numpy as np
import itertools
import networkx as nx
from pprint import pformat
from collections import Counter

from interactions import InteractionsUtil as IU
from util import load_summary_related_data


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
                  for i in self.g.nodes()]
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
        nodes = self.g.nodes()
        in_degrees = np.asarray([self.g.in_degree(n)
                                 for n in nodes],
                                dtype=np.int64)
        out_degrees = np.asarray([self.g.out_degree(n)
                                  for n in nodes],
                                 dtype=np.int64)
        degrees = in_degrees + out_degrees

        root_indices = np.nonzero(np.logical_and(in_degrees == 0,
                                                 out_degrees > 0))[0]
        roots = [nodes[i] for i in root_indices]
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
            },
            'roots': sorted(roots)
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
                    IU.tokenize_document(id2msg[id_])
                ),
                minimum_probability=0
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
            id2msg[m['message_id']] = u"{} {}".format(
                m['subject'], m['body']
            )

        # topic_dist
        message_ids = [self.g.node[n]['message_id']
                       for n in self.g.nodes()]
        concated_msg = ' '.join([id2msg[mid] for mid in message_ids])
        bow = dictionary.doc2bow(IU.tokenize_document(concated_msg))
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

    def participants(self, people_info, interactions,
                     people_repr_template="{name}({email})",
                     undirected=False,
                     top_k=10):
        peopleid2info = {r['id']: people_repr_template.format(**r)
                         for r in people_info}
        id2interaction = {i['message_id']: i
                          for i in interactions}
        result = {}
        if not undirected:
            def populate_user_info(counter):
                data = dict(map(lambda (people_id, count):
                                (peopleid2info[people_id], count),
                                counter.items()))
                return Counter(data)

            result['sender_count'] = Counter(
                [id2interaction[self.g.node[n]['message_id']]['sender_id']
                 for n in self.g.nodes()]
            )

            result['sender_count'] = populate_user_info(result['sender_count'])

            result['recipient_count'] = Counter([
                r
                for n in self.g.nodes()
                for r in \
                id2interaction[self.g.node[n]['message_id']]['recipient_ids']
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
            
            for key in ('sender_count', 'recipient_count',
                        'participant_count'):
                result[key] = sorted(result[key].items(),
                                     key=lambda (info, c): (c, info),
                                     reverse=True)[:top_k]
            
        else:
            cnt = Counter(
                itertools.chain(
                    *[id2interaction[self.g.node[n]['message_id']]['participant_ids']
                      for n in self.g.nodes_iter()
                  ]
                ))
            result['participant_count'] = sorted(cnt.items(),
                                                 key=lambda (_, c): (c, _),
                                                 reverse=True)[:top_k]
        return result

    def link_type_freq(self, interactions, undirected=False):
        if not undirected:
            id2i = {}
            for m in interactions:
                id2i[m['message_id']] = m

            counter = Counter()
            for k in ('broadcast', 'reply', 'relay'):
                counter[k] = 0
            for s, t in self.g.edges_iter():
                src_sender_id, src_recipient_ids = id2i[s]['sender_id'],\
                                                   set(id2i[s]['recipient_ids'])
                tar_sender_id, tar_recipient_ids = id2i[t]['sender_id'],\
                                                   set(id2i[t]['recipient_ids'])
                if src_sender_id == tar_sender_id:
                    counter['broadcast'] += 1
                elif tar_sender_id in src_recipient_ids:
                    if src_sender_id in tar_recipient_ids:
                        counter['reply'] += 1
                    else:
                        counter['relay'] += 1
                else:
                    raise ValueError('Invalid lin type')
            return dict(counter)
        else:
            return 'not available for undirected graph'

    def summary_dict(self):
        return {m: getattr(self, m)(**self.kws[m])
                for m in self.kws.keys()
                if callable(getattr(self, m))
        }

    def summary(self):
        return pformat(self.summary_dict())


def build_default_summary_kws(interactions, people_info,
                              dictionary, lda, people_repr_template,
                              undirected=False):
    interactions = IU.clean_interactions(interactions,
                                         undirected=undirected)
    summary_kws = {
        'basic_structure_stats': {},
        'time_span': {},
        'topics': {
            'interactions': interactions,
            'dictionary': dictionary,
            'lda': lda,
            'top_k': 10
        },
        'email_content': {
            'interactions': interactions,
            'top_k': 5
        },
        'participants': {
            'people_info': people_info,
            'interactions': interactions,
            'top_k': 5,
            'people_repr_template': people_repr_template,
            'undirected': undirected
        },
        'link_type_freq': {
            'interactions': interactions,
            'undirected': undirected
        }
    }
    return summary_kws


def build_default_summary_kws_from_path(
        interactions_path, people_path,
        corpus_dict_path, lda_model_path, people_repr_template,
        **kwargs):
    return build_default_summary_kws(
        *load_summary_related_data(
            interactions_path, people_path,
            corpus_dict_path, lda_model_path
        ),
        people_repr_template=people_repr_template,
        **kwargs
    )
    
