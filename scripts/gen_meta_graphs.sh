#! /bin/bash

common="--lda=models/model-25-100.lda --weeks=8 --res_dir=tmp/lda-25-topics"

dist_funcs=("cosine" "euclidean")

for dist_func in "${dist_funcs[@]}"
do
    base="python gen_candidate_trees.py --dist ${dist_func} --calc_mg --cand_n 0 --method random ${common}"
    eval $base
    eval "${base} --decompose"
done

# python gen_candidate_trees.py --dist euclidean --calc_mg --cand_n 0 --method random  ${common}
