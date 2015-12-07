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

trees = pkl.load(open('tmp/binary_rooted_tree_samples.pkl'))

U = 0.5

names = [# 'lst(round)', 
         'lst(ceil)', 'lst(floor)', 
         # 'greedy'
]

funcs = [lambda g, r, U, func=func: lst_dag(g, r, U,
                                            fixed_point_func=func,
                                            debug=False,
                                            edge_weight_decimal_point=2)
         for func in (# round,
                      ceil, 
                      floor)]
# funcs.append(greedy_grow)

# t = trees[5]

# from lst import round_edge_weights_by_multiplying

# g_ceil, U = round_edge_weights_by_multiplying(t, U, 2, fixed_point_func=ceil)
# g_floor, U = round_edge_weights_by_multiplying(t, U, 2, fixed_point_func=floor)
# print(U)
# for u, v in g_ceil.edges():
#     if 'dummy' not in g_ceil.node[v]:
#         print("original: {}, ceil: {}, floor: {}".format(
#             t[u][v]['c'],
#             g_ceil[u][v]['c'],
#             g_floor[u][v]['c'])
#           )
# import sys
# sys.exit(-1)

for i, t in enumerate(trees):
    if i != 5:
        continue
    print('Tree: {}'.format(i+1))
    roots = get_roots(t)
    assert len(roots) == 1
    root = roots[0]

    print(get_meta_graph_stat(t).summary())
    sub_trees = []
    for name, func in zip(names, funcs):
        # sub_t = unbinarize_dag(
        #     func(t, root, U),
        #     'c'
        # )
        sub_t = func(t, root, U)
        sub_trees.append(sub_t)
        print(sub_t.nodes())
        print(sub_t.edges())
        # stat = get_meta_graph_stat(sub_t)['basic_structure_stats']
        # print(stat)
        # import pdb;
        # pdb.set_trace()

        nodes_n = len(sub_t.nodes())
        edges_n = len(sub_t.edges())

        cs = [sub_t[u][v]['c'] for u, v in sub_t.edges()]
        print(cs)
        print(sum(cs))

        print('{}: {}, {}'.format(name, nodes_n, edges_n))
        print('\n')
    edges_to_remain = set([e
                           for sub_t in sub_trees
                           for e in sub_t.edges()])
    total_edges = set(t.edges())
    assert edges_to_remain.issubset(total_edges)
    edges_to_remove = total_edges - edges_to_remain
    print('original len(t.edges)', len(t.edges()))
    print('removing {} edges'.format(len(edges_to_remove)))
    t.remove_edges_from(edges_to_remove)
    print('current len(t.edges)', len(t.edges()))
    ceil_t = funcs[0](t, root, U)
    floor_t = funcs[1](t, root, U)
    print('ceil_t: {}, floor_t: {}'.format(
        len(ceil_t.edges()),
        len(floor_t.edges()))
    )
    print()
