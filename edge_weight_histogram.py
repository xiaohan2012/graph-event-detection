import matplotlib as mpl
mpl.use('Agg')

import numpy as np
import cPickle as pkl
import matplotlib.pyplot as plt

from experiment_util import experiment_signature
from meta_graph_stat import MetaGraphStat

DIST_FUNC = "cosine"

STAT_KWS = {
    'temporal_traffic': False,
    'topics': False,
    'email_content': False,
    'participants': False,
    'edge_costs': {
        'max_values': [1.0, 0.1, 1e-2, 1e-4, 1e-5, 1e-13, 1e-14, 1e-12]
    }
}


def get_summary(g):
    return MetaGraphStat(g, STAT_KWS).summary_dict()

sig = experiment_signature(decompose_interactions=False, dist_func=DIST_FUNC)
enron_pickle_path = "data/enron--{}.pkl".format(sig)


g = pkl.load(open(enron_pickle_path))

hists = get_summary(g)['edge_costs']

fig, axs = plt.subplots(len(hists), 1, figsize=(25, 30))
axs = axs.ravel()

for i, (name, hist_data) in enumerate(sorted(hists.items())):
    print(i, name)
    freq, bins = hist_data
    left = np.arange(len(freq))
    axs[i].bar(left, freq)
    ticklabels = map(lambda n: '{:.9f}'.format(n), bins[1:])
    print(ticklabels)

    plt.sca(axs[i])
    plt.xticks(left+1, ticklabels)

    # axs[i].set_xticklabels(ticklabels)
    
    axs[i].set_title(name)

fig.subplots_adjust(bottom=0.15)

fig.savefig('figures/hist-{}.png'.format(sig))
