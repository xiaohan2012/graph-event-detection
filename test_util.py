import matplotlib
# Force matplotlib to not use any Xwindows backend.
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import os
import gensim
import ujson as json
import glob
import networkx as nx
from nose.tools import assert_equal, assert_true, assert_raises
from datetime import datetime
from interactions import InteractionsUtil as IU


from util import to_d3_graph, get_datetime


CURDIR = os.path.dirname(os.path.abspath(__file__))


def load_meta_graph_necessities(lda_path='test/data/test.lda',
                                dictionary_path='test/data/test_dictionary.gsm',
                                interactions_path='test/data/enron_test.json'):
    lda_model = gensim.models.ldamodel.LdaModel.load(
        os.path.join(CURDIR, lda_path)
    )
    dictionary = gensim.corpora.dictionary.Dictionary.load(
        os.path.join(CURDIR, dictionary_path)
    )
    interactions = json.load(
        open(os.path.join(CURDIR,
                          interactions_path)))
    return lda_model, dictionary, interactions


def draw_example_meta_graph(output_path):
    _, _, ints = load_meta_graph_necessities()
    g = IU.get_meta_graph(
        ints,
        decompose_interactions=True
    )
    plt.clf()
    pos = nx.spring_layout(g)
    nx.draw_networkx_nodes(g, pos=pos)
    nx.draw_networkx_edges(g, pos=pos)
    nx.draw_networkx_labels(g, pos=pos,
                            labels=dict(zip(g.nodes(), g.nodes())),
                            font_size=8)
    plt.savefig(output_path)

def remove_tmp_data(directory):
    # remove the pickles
    files = glob.glob(os.path.join(CURDIR,
                                   "{}/*".format(directory)))
    for f in files:
        os.remove(f)


def test_to_d3_graph():
    g = nx.DiGraph()
    g.add_nodes_from(['a', 'b', 'c'])
    g.add_edges_from([('a', 'b'), ('b', 'c'), ('c', 'a')])
    for n in g.nodes_iter():
        g.node[n]['attr1'] = 'attr1'
        g.node[n]['attr2'] = 'attr2'

    for s, t in g.edges_iter():
        g[s][t]['der1'] = 'der1'
        g[s][t]['der2'] = 'der2'

    d3_g = to_d3_graph(g)
    assert_equal(sorted([{'name': 'a', 'attr1': 'attr1', 'attr2': 'attr2'},
                         {'name': 'b', 'attr1': 'attr1', 'attr2': 'attr2'},
                         {'name': 'c', 'attr1': 'attr1', 'attr2': 'attr2'}
                     ]),
                 sorted(d3_g['nodes'])
    )
    assert_equal(3, len(d3_g['edges']))
    assert_equal(
        sorted([{'source': 0, 'target': 2, 'der1': 'der1', 'der2': 'der2'},
                {'source': 2, 'target': 1, 'der1': 'der1', 'der2': 'der2'},
                {'source': 1, 'target': 0, 'der1': 'der1', 'der2': 'der2'}
            ]),
        sorted(d3_g['edges'])
    )


def test_get_datetime():
    data = [994832962,
            '2004-04-28 00:00:00.000',
            '2004-04-28 00:00:00',
            datetime.fromtimestamp(994832962)]
    for d in data:
        assert_true(
            isinstance(get_datetime(d),
                       datetime)
        )

    assert_raises(TypeError, get_datetime, dict())
    assert_raises(ValueError, get_datetime, 'bad formatsadfasfd')


