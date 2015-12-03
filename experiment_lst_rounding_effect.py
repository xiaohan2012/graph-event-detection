# Comparison on
# Effects of round, floor, ceil during the fix-point approximation of lst_dag


import cPickle as pkl
from math import ceil, floor


from lst import lst_dag
from baselines import greedy_grow
from dag_util import unbinarize_dag
from graph_util import get_roots
from meta_graph_stat import MetaGraphStat


KWs = {
    'temporal_traffic': False,
    'topics': False,
    'email_content': False,
    'time_span': False,
    'participants': False
}


def get_meta_graph_stat(g):
    return MetaGraphStat(g, KWs)

g = pkl.load(open('data/enron.pkl'))
trees = pkl.load(open('tmp/binary_rooted_tree_samples.pkl'))
U = 0.5

names = ['lst(round)', 'lst(ceil)', 'lst(floor)', 'greedy']

funcs = [lambda g, r, U, func=func: lst_dag(g, r, U,
                                            fixed_point_func=func,
                                            edge_weight_decimal_point=2)
         for func in (round, ceil, floor)]
funcs.append(greedy_grow)


for i, t in enumerate(trees):
    if i != 1:
        continue
    print('Tree: {}'.format(i+1))
    roots = get_roots(t)
    assert len(roots) == 1
    root = roots[0]
    
    print(get_meta_graph_stat(t).summary())
    for name, func in zip(names, funcs):
        sub_t = unbinarize_dag(
            func(t, root, U),
            'c'
        )
        # nodes_n = get_meta_graph_stat(sub_t)['basic_structure_stats']['#nodes']
        # import pdb;
        # pdb.set_trace()
        
        nodes_n = len(sub_t.nodes())
        
        cs = [sub_t[u][v]['c'] for u, v in sub_t.edges()]
        print(cs)
        print(sum(cs))

        print('{}: {}'.format(name, nodes_n))
    
    print()
