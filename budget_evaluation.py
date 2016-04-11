import pandas as pd
import numpy as np
import cPickle as pkl
from glob import glob
from synthetic_evaluation import  group_paths
from check_k_best_trees import k_best_trees
from experiment_util import parse_result_path


def eval_setcover_obj_func(cand_trees, k):
    trees = k_best_trees(cand_trees, k)
    return len(set(n for t in trees for n in t.nodes_iter()))

def eval_tree_size_obj_mean(cand_trees):
    sizes = [t.number_of_nodes() for t in cand_trees]
    return np.mean(sizes)

def eval_tree_size_obj_median(cand_trees):
    sizes = [t.number_of_nodes() for t in cand_trees]
    return np.median(sizes)

def eval_calculation_time(cand_trees):
    return sum(t.graph['calculation_time'] for t in cand_trees)

    
def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--experiment_paths_regexp')
    parser.add_argument('-k', type=int)
    parser.add_argument('-o', '--output_path', required=True)

    args = parser.parse_args()
    
    paths = glob(args.experiment_paths_regexp)
    # print(args.experiment_paths_regexp)
    # print(paths)
    groups_by_method = group_paths(paths,
                                   keyfunc=lambda p: p['args'][0],
                                   sort_keyfunc=lambda k: float(k['U']))
    # print(len(groups_by_method))
    setcover_obj_mat = []
    calculation_time_mat = []
    tree_size_obj_mean_mat = []
    tree_size_obj_median_mat = []

    index = []
    for method, paths in groups_by_method:
        index.append(method)
        results = [pkl.load(open(p)) for p in paths]
        setcover_obj_mat.append([eval_setcover_obj_func(ctrees, args.k)
                             for ctrees in results])
        calculation_time_mat.append([eval_calculation_time(ctrees)
                                     for ctrees in results])
        tree_size_obj_mean_mat.append([eval_tree_size_obj_mean(ctrees)
                                       for ctrees in results])
        tree_size_obj_median_mat.append([eval_tree_size_obj_median(ctrees)
                                       for ctrees in results])
        
    print('index:', index)
    columns = [float(parse_result_path(p)['U'])
               for p in paths]
    print(columns)
    print(np.asarray(setcover_obj_mat).shape)
    print(np.asarray(tree_size_obj_mean_mat).shape)
    df1 = pd.DataFrame(setcover_obj_mat,
                       index=index,
                       columns=columns)
    df2 = pd.DataFrame(calculation_time_mat,
                       index=index,
                       columns=columns)
    df3 = pd.DataFrame(tree_size_obj_mean_mat,
                       index=index,
                       columns=columns)
    df4 = pd.DataFrame(tree_size_obj_median_mat,
                       index=index,
                       columns=columns)

    ret = {
        'setcover-objective': df1,
        'calculation-time': df2,
        'treesize-objective-mean': df3,
        'treesize-objective-median': df4
        }

    pkl.dump(ret, open(args.output_path, 'w'))
    
    
if __name__ == "__main__":
    main()
