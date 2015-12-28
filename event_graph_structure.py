import os
import numpy as np
import matplotlib
# Force matplotlib to not use any Xwindows backend.
matplotlib.use('Agg')

import matplotlib.pyplot as plt

from networkx.drawing.nx_pylab import draw_spring

from meta_graph import convert_to_original_graph
from events import detect_events_given_path
from util import load_json_by_line

CURDIR = os.path.dirname(os.path.abspath(__file__))

interactions = load_json_by_line(CURDIR + '/data/enron.json')

people_info = load_json_by_line(CURDIR + '/data/people.json')
peopleid2info = {r['id']: (r['name'], r['email'])
                 for r in people_info}
summary_kws = {
    'temporal_traffic': False,
    'topics': False,
    'email_content': False,
    'participants': {
        'people_info': people_info,
        'interactions': interactions
    }
}


def draw_kws_graphs(g):
    degrees_dict = g.degree(g.nodes())
    degrees = [degrees_dict[n] for n in g.nodes()]
    return {
        'node_size': np.log(np.asarray(degrees) + 1) * 100
    }


def draw_kws_events(g):
    data = draw_kws_graphs(g)
    nodes = g.nodes()
    degrees = g.degree(nodes)
    important_nodes = sorted(nodes, key=lambda k: degrees[k], reverse=True)[:3]
    data['labels'] = {n: peopleid2info[n]
                      for n in important_nodes}
    data.update({'font_size': 16,
                 'font_weight': 'bold',
                 'font_color': '#2980B9'})
    return data


def plot_events(events, figure_dir):
    """for original graph
    """
    gs = map(convert_to_original_graph, events)
    plot_graphs(gs, figure_dir, gen_kws_func=draw_kws_events)


def plot_graphs(gs, figure_dir, gen_kws_func=draw_kws_graphs):
    """more meta graph
    """
    if not os.path.exists(figure_dir):
        os.makedirs(figure_dir)
    for i, g in enumerate(gs):
        kws = gen_kws_func(g)
        draw_spring(g, **kws)
        plt.hold(False)
        plt.savefig(os.path.join(figure_dir, "{}.png".format(i+1)))


def main():
    import sys
    result_path = sys.argv[1]
    dirname = os.path.basename(result_path).replace('.pkl', '')
    events = detect_events_given_path(result_path, 5)
    # plot_graphs(events, 'figures/{}'.format(dirname))
    plot_events(events, 'figures/original-graph-of-event/{}'.format(dirname))
    
if __name__ == '__main__':
    main()
