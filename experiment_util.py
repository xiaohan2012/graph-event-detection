import numpy as np
import networkx as nx
import cPickle as pkl
from datetime import timedelta


from enron_graph import EnronUtil
from dag_util import binarize_dag


def sample_nodes(g, node_sample_size=100):
    nodes = g.nodes()
    return [nodes[i]
            for i in np.random.permutation(len(g.nodes()))[:node_sample_size]]


def sample_rooted_binary_graphs_within_timespan(
        meta_graph_pickle_path,
        sample_number,
        timespan,
        output_path):
    g = nx.read_gpickle(meta_graph_pickle_path)
    roots = sample_nodes(g, sample_number)
    results = []
    for i, r in enumerate(roots):
        print('done:', i)
        sub_g = EnronUtil.get_rooted_subgraph_within_timespan(
            g, r, timespan, debug=False
        )
        binary_sub_g = binarize_dag(sub_g,
                                    EnronUtil.VERTEX_REWARD_KEY,
                                    EnronUtil.EDGE_COST_KEY,
                                    dummy_node_name_prefix="d_")
        
        if len(binary_sub_g.edges()) > 0:
            results.append(binary_sub_g)

    pkl.dump(results, open(output_path, 'w'))


def experiment_signature(**kws):
    def value_str(v):
        if callable(v):
            return v.__name__
        elif isinstance(v, timedelta):
            return '{}days'.format(v.days)
        else:
            return str(v)

    return '--'.join(["{}={}".format(k, value_str(v))
                      for k, v in sorted(kws.items())])

if __name__ == '__main__':
    sample_rooted_binary_graphs_within_timespan(
        meta_graph_pickle_path='data/enron.pkl',
        sample_number=20,
        timespan=timedelta(weeks=4).total_seconds(),
        output_path='tmp/binary_rooted_tree_samples.pkl'
    )
