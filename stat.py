import numpy as np
from pprint import pformat
from collections import OrderedDict


class MetaGraphStat(object):
    def __init__(self, g):
        self.g = g

    def time_span(self):
        ds = [self.g.node[i]['datetime'] for i in self.g.nodes()]
        return {'start_time': min(ds), 
                'end_time': max(ds)}
        
    def basic_structure_stats(self):
        in_degrees = np.asarray([self.g.in_degree(n)
                                 for n in self.g.nodes()],
                                dtype=np.int64)
        out_degrees = np.asarray([self.g.out_degree(n)
                                  for n in self.g.nodes()],
                                 dtype=np.int64)
        
        return {
            '#nodes': len(self.g.nodes()),
            '#edges': len(self.g.edges()),
            'in_degree': {
                'min': in_degrees.min(),
                'max': in_degrees.max(),
                'average': in_degrees.mean(),
                'median': np.median(in_degrees)
            },
            'out_degree': {
                'min': out_degrees.min(),
                'max': out_degrees.max(),
                'average': out_degrees.mean(),
                'median': np.median(out_degrees)
            }
        }

    def summary(self):
        return pformat(
            {m: getattr(self, m)()
             for m in dir(self)
             if not m.startswith('_') and m != 'summary' and callable(getattr(self, m))})

