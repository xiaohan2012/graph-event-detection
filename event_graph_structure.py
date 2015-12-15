import os
import numpy as np
import matplotlib
# Force matplotlib to not use any Xwindows backend.
matplotlib.use('Agg')

import matplotlib.pyplot as plt

from networkx.drawing.nx_pylab import draw_spring

from meta_graph import convert_to_original_graph


def draw_kws(g):
    degrees = g.degree(g.nodes()).values()
    return {'node_size': np.log(np.asarray(degrees) + 1) * 100}


def plot_events(events, figure_dir):
    """for original graph
    """
    gs = map(convert_to_original_graph, events)
    plot_graphs(gs, figure_dir)


def plot_graphs(gs, figure_dir):
    """more meta graph
    """
    if not os.path.exists(figure_dir):
        os.makedirs(figure_dir)
    for i, g in enumerate(gs):
        kws = draw_kws(g)
        draw_spring(g, **kws)
        plt.savefig(os.path.join(figure_dir, "{}.png".format(i+1)))

# result_path = 'tmp/result-example.pkl'
# events = detect_events_given_path(result_path, 5)
# plot_graphs(events, 'figures/structure-example')
