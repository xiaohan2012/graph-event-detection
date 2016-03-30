import matplotlib as mpl
mpl.use('Agg')

import matplotlib.pyplot as plt
import cPickle as pkl
import networkx as nx
from dag_util import get_roots
from budget_problem import binary_search_using_charikar

g = pkl.load(open('test/data/tmp/result-quota--U=0.01--dijkstra=False--timespan=28days----consider_recency=False--distance_weights={"topics":1.0}--preprune_secs=28days----cand_tree_percent=0.1--root_sampling=random.pkl.dag'))[2]
print('g.has_edge(54619, 54627)', g.has_edge(54619, 54627))

root = get_roots(g)[0]

print('roots:', get_roots(g))

nodes_to_remove = [54637, 54657, 54677, 54669, 54643,
                   54640, 54631, 54627, 54673, 54670,
                   54647]

# for n in g.nodes_iter():
#     if g.in_degree(n) == 0 and n != root:
#         nodes_to_remove.append(n)
        
print(nodes_to_remove)

for n in nodes_to_remove:
    g.remove_node(n)



# pos = nx.graphviz_layout(g, prog='dot')

# nx.draw(g, pos,
#         node_color=map(lambda n: 'black' if n == root else 'gray',
#                        g.nodes_iter())
#     )
# nx.draw_networkx_labels(g,
#                         pos=pos,
#                         labels={n: str(n) for n in g.nodes_iter()},
#                         font_color='red'
# )

# plt.savefig(
#     '/cs/home/hxiao/public_html/figures/tree_inspection/{}.png'.format(root)
# )

quota_based_method = lambda g, r, U: binary_search_using_charikar(
    g, r, U, level=2
)

quota_based_method(g, root, 1.0)
