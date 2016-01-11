import networkx as nx
import gensim
from datetime import datetime

from nose.tools import assert_equal

from .dump_vis_timeline_data import run
from .test_util import make_path
from .meta_graph_stat import MetaGraphStat, build_default_summary_kws


def test_dump():
    k = 2

    def make_graph(nodes):
        g = nx.DiGraph()
        g.add_nodes_from(nodes)
        g.add_path(nodes)
        for n in g.nodes_iter():
            g.node[n]['message_id'] = n
        return g

    trees = [make_graph([1, 2]), make_graph([1, 3, 4])]

    trees[0].node[1]['datetime'] = datetime(2014, 01, 30)
    trees[0].node[2]['datetime'] = datetime(2014, 01, 18)
    trees[1].node[1]['datetime'] = datetime(2014, 01, 30)  # dup
    trees[1].node[3]['datetime'] = datetime(2014, 01, 21)
    trees[1].node[4]['datetime'] = datetime(2014, 01, 17)

    def make_message(id, sender_id, recipient_id, subject, dt):
        return {
            'message_id': id,
            'sender_id': sender_id,
            'recipient_ids': [recipient_id],
            'subject': subject,
            'body': '',
            'datetime': datetime(*dt)
        }
    summary_kws = build_default_summary_kws(
        [
            make_message(1, 'a', 'b', 'item 1', (2014, 01, 30)),
            make_message(2, 'b', 'a', 'item 2', (2014, 01, 18)),
            make_message(3, 'a', 'c', 'item 3', (2014, 01, 21)),
            make_message(4, 'c', 'a', 'item 4', (2014, 01, 17)),
        ],
        [
            {'id': 'a'},
            {'id': 'b'},
            {'id': 'c'}
        ],
        gensim.corpora.dictionary.Dictionary.load(
            make_path('test/data/test_dictionary.gsm')
        ),
        gensim.models.ldamodel.LdaModel.load(
            make_path('test/data/test.lda')
        ),
        "{id}"
    )
    summary_kws['edge_costs'] = False
    summaries = [MetaGraphStat(t, summary_kws).summary_dict()
                 for t in trees]

    assert_equal.__self__.maxDiff = None

    actual = run(trees, k, summary_kws)
    expected = {
        'items': [
            {'id': 1, 'content': 'item 1',
             'start': '2014-01-30', 'group': 1},
            {'id': 2, 'content': 'item 2',
             'start': '2014-01-18', 'group': 1},
            {'id': 3, 'content': 'Event 1',
             'start': '2014-01-18', 'end': '2014-01-30',
             'type': 'background', 'group': 1},
            {'id': 4, 'content': 'item 1',
             'start': '2014-01-30', 'group': 2},
            {'id': 5, 'content': 'item 3',
             'start': '2014-01-21', 'group': 2},
            {'id': 6, 'content': 'item 4',
             'start': '2014-01-17', 'group': 2},
            {'id': 7, 'content': 'Event 2',
             'start': '2014-01-17', 'end': '2014-01-30',
             'type': 'background', 'group': 2}
        ],
            'groups': [
                {
                    'id': 1,
                    'terms': list(summaries[0]['topics']['topic_terms']),
                    'participants': dict(
                        summaries[0]['participants']['sender_count']
                    )
                },
                {
                    'id': 2,
                    'terms': summaries[1]['topics']['topic_terms'],
                    'participants': dict(
                        summaries[1]['participants']['sender_count']
                    )
                }
            ],
            'start': '2014-01-17',
        'end': '2014-01-30',
    }
    # wierd just because terms are not the same...
    assert_equal(expected['items'], actual['items'])
    assert_equal(expected['start'], actual['start'])
    assert_equal(expected['end'], actual['end'])
    for eg, ag in zip(expected['groups'], actual['groups']):
        assert_equal(eg['id'], ag['id'])
        assert_equal(len(eg['terms']), len(ag['terms']))
        assert_equal(len(eg['participants']), len(ag['participants']))

