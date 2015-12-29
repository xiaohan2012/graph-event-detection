#! /bin/bash



common="--lda_path=data/islamic/model-100-50.lda --weeks=4 --res_dir=tmp/islamic/ --interaction_path=data/islamic/interactions.json --corpus_dict_path=data/islamic/dict.pkl --meta_graph_path_prefix=tmp/islamic/meta-graph"

dist_funcs=(# "cosine"
    "euclidean")

for dist_func in "${dist_funcs[@]}"
do
    base="python gen_candidate_trees.py --dist ${dist_func} --calc_mg --cand_n 0 --method random ${common}"
    echo $base
    # eval "${base} --decompose"
done

# python gen_candidate_trees.py --dist euclidean --calc_mg --cand_n 0 --method random  ${common}
