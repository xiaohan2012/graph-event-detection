import matplotlib as mpl
mpl.use('Agg')

import networkx as nx
import cPickle as pkl
import matplotlib.pyplot as plt
from collections import defaultdict

from check_k_best_trees import k_best_trees


def draw(mg, trees, output_path):
    involed_users = set(n['sender_id'] for t in trees for n in t.nodes_iter())
    people_network = nx.Graph()
    for n in mg.nodes_iter():
        sender = mg.node[n]['sender_id']
        recipients = mg.node[n]['recipient_ids']
        people_network.add_edges_from([(sender, r) for r in recipients])

    print('people_network.number_of_nodes():',
          people_network.number_of_nodes())
    colors = ['red', 'blue', 'green', 'yellow', 'black', 'orange']
    colors = defaultdict(lambda: 'gray')
    for c, t in zip(colors, trees):
        for n in t.nodes_iter():
            colors[n] = c
    pos = nx.spring_layout(people_network)
    nx.draw_networkx(people_network, pos)
    nx.draw_networkx_nodes(people_network,
                           pos,
                           node_color=colors)
    plt.savefig(output_path)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--meta_graph_path')
    parser.add_argument('-r', '--result_path')
    parser.add_argument('-k', '--k', type=int)
    parser.add_argument('-o', '--output_path')

    args = parser.parse_args()

    draw(nx.read_gpickle(args.meta_graph_path),
         k_best_trees(pkl.load(open(args.result_path)), args.k),
         args.output_path)
