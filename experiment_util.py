import os
import re
import numpy as np
import networkx as nx
import cPickle as pkl
from datetime import timedelta
import random

from interactions import InteractionsUtil
from dag_util import binarize_dag


def sample_nodes(g, node_sample_size=100):
    nodes = g.nodes()
    return [nodes[i]
            for i in np.random.permutation(len(g.nodes()))[:node_sample_size]]


def weighted_choice(choices):
    """choices: list of (element, weight)
    """
    total = sum(w for c, w in choices)
    r = random.uniform(0, total)
    upto = 0
    for c, w in choices:
        if upto + w >= r:
            return (c, w)
        upto += w
    assert False, "Shouldn't get here"


def sample_nodes_by_weight(g, weight_func, node_sample_size=100):
    choices = set(
        [(n, weight_func(n))
         for n in g.nodes_iter() if weight_func(n) > 0]
    )
    samples = []
    if node_sample_size >= len(choices):
        return g.nodes()
    else:
        while len(samples) < node_sample_size:
            c, w = weighted_choice(choices)
            samples.append(c)
            choices.remove((c, w))
        return samples


def sample_nodes_by_out_degree(g, node_sample_size=100):
    return sample_nodes_by_weight(g,
                                  weight_func=lambda n: g.out_degree(n),
                                  node_sample_size=node_sample_size)


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
        sub_g = InteractionsUtil.get_rooted_subgraph_within_timespan(
            g, r, timespan, debug=False
        )
        binary_sub_g = binarize_dag(sub_g,
                                    InteractionsUtil.VERTEX_REWARD_KEY,
                                    InteractionsUtil.EDGE_COST_KEY,
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


def get_output_path(candidate_tree_path, dirname=None):
    output_name = os.path.basename(
        candidate_tree_path).replace('.pkl', '.json')
    if dirname:
        output_path = os.path.join(dirname, output_name)
    else:
        output_path = os.path.join(os.path.dirname(candidate_tree_path),
                                   output_name)
    return output_path


def get_number_and_percentage(total, n, percentage):
    if n == -1:
        return (total, 1.0)
    elif n is not None and n > 0:
        if n >= total:
            return (total, 1.0)
        else:
            return (n, float(n) / total)
    else:
        assert isinstance(percentage, float)
        return (int(total*percentage), percentage)


def parse_result_path(path):
    ret = {'args': []}
    path = os.path.splitext(os.path.basename(path))[0]
    path = re.sub(r'result[-]{1,2}', '', path)
    for sub in re.split(r'[-]{2,4}', path):
        if '=' in sub:
            k, v = sub.split('=')
            ret[k] = v
        else:
            ret['args'].append(sub)
    return ret


if __name__ == '__main__':
    sample_rooted_binary_graphs_within_timespan(
        meta_graph_pickle_path='data/enron.pkl',
        sample_number=20,
        timespan=timedelta(weeks=4).total_seconds(),
        output_path='tmp/binary_rooted_tree_samples.pkl'
    )
