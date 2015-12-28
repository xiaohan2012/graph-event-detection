import sys
import pandas as pds
from tabulate import tabulate
from glob import glob
import cPickle as pickle

# from tabulate import tabulate

from max_cover import argmax_k_coverage


# name path name path
# names = [name for i, name in enumerate(sys.argv[1:]) if i % 2 == 0]
# paths = [path for i, path in enumerate(sys.argv[1:]) if i % 2 == 1]
paths = glob("tmp/lda-25-topics/result-*U=5*interactions=False*.pkl")
names = map(lambda n:
            n.replace('tmp/lda-25-topics/result-', '').replace('.pkl', ''),
            paths)

K = 5

table = []
for name, path in zip(names, paths):
    trees = pickle.load(open(path))
    nodes_of_trees = [set(t.nodes()) for t in trees]
    selected_ids = argmax_k_coverage(nodes_of_trees, K)
    selected_trees = [trees[i] for i in selected_ids]
    nodes_list = [t.nodes() for t in selected_trees]
    unique_nodes = reduce(lambda acc, nodes: acc | set(nodes),
                          nodes_list,
                          set())

    row = [name]
    row += [len(nodes) for nodes in nodes_list]
    row.append(len(unique_nodes))
    
    table.append(row)

df = pds.DataFrame(table, columns=['', '#1', '#2', '#3', '#4', '#5', 'total'])

print(tabulate(df.sort(['total'], ascending=False),
               headers=list(df.columns),
               tablefmt='psql'))

# print tabulate(table, headers=['', '#1', '#2', '#3', '#4', '#5', 'total'],
#                tablefmt='orgtbl')
