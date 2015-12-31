import networkx as nx
from datetime import datetime
from nose.tools import assert_true, assert_equal

from .event_context import extract_event_context
from .test_util import load_meta_graph_necessities
from .interactions import InteractionsUtil as IU


def load_example():
    _, _, interactions = load_meta_graph_necessities()
        
    # some fake interactions
    for i in xrange(100):
        interactions.append({"body": "...",
                             "recipient_ids": ["F"],
                             "sender_id": "A",
                             "datetime": 989587577,
                             "message_id": len(interactions)+1,
                             "subject": "..."}
        )
    interactions = IU.clean_interactions(interactions)

    event_tree = nx.DiGraph()
    event_tree.add_nodes_from(
        [(0, {'datetime': datetime.fromtimestamp(989587576)}),
         (1, {'datetime': datetime.fromtimestamp(989587577)}),
         (2, {'datetime': datetime.fromtimestamp(989587578)})]
    )
    event_tree.add_edges_from([(0, 1), (1, 2)])

    return interactions, event_tree


def test_extract_event_context():
    interactions, event_tree = load_example()

    context_dag = extract_event_context(interactions, event_tree)

    assert_true(isinstance(context_dag, nx.DiGraph))
    assert_equal(103, context_dag.number_of_nodes())
    nodes_set = set(context_dag.nodes())
    for i in (range(1, 4) + range(7, 107)):
        assert_true(i in nodes_set)
    
