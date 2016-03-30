import pandas as pd
import cPickle as pkl
from glob import glob
from synthetic_evaluation import  group_paths
from check_k_best_trees import k_best_trees
from experiment_util import parse_result_path


def eval_obj_func(cand_trees, k):
    trees = k_best_trees(cand_trees, k)
    return len(set(n for t in trees for n in t.nodes_iter()))


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
    obj_func_mat = []
    calculation_time_mat = []
    
    index = []
    for method, paths in groups_by_method:
        index.append(method)
        obj_func_mat.append([eval_obj_func(pkl.load(open(p)), args.k)
                             for p in paths])
        calculation_time_mat.append([eval_calculation_time(pkl.load(open(p)))
                                     for p in paths])
        
    print('index:', index)
    columns = [float(parse_result_path(p)['U'])
               for p in paths]
    df1 = pd.DataFrame(obj_func_mat,
                       index=index,
                       columns=columns)
    df2 = pd.DataFrame(calculation_time_mat,
                       index=index,
                       columns=columns)
    ret = {
        'objective_function': df1,
        'calculation_time': df2
        }

    pkl.dump(ret, open(args.output_path, 'w'))
    
    
if __name__ == "__main__":
    main()
