import os
import gensim
import ujson as json
import glob
import networkx as nx
from nose.tools import assert_equal, assert_true, assert_raises
from datetime import datetime

from .util import to_d3_graph, get_datetime


CURDIR = os.path.dirname(os.path.abspath(__file__))


def load_meta_graph_necessities():
    lda_model = gensim.models.ldamodel.LdaModel.load(
        os.path.join(CURDIR, 'test/data/test.lda')
    )
    dictionary = gensim.corpora.dictionary.Dictionary.load(
        os.path.join(CURDIR, 'test/data/test_dictionary.gsm')
    )
    interactions = json.load(
        open(os.path.join(CURDIR,
                          'test/data/enron_test.json')))
    return lda_model, dictionary, interactions


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

