#! /bin/bash

methods=("lst" "greedy" "random")
dist_funcs=("euclidean")

common_params="--U=0.05 --lda=models/model-25-100.lda --weeks=8 --res_dir=tmp/lda-25-topics"

for dist_func in "${dist_funcs[@]}"
do
	for method in "${methods[@]}"
	do
		echo "python gen_candidate_trees.py --method ${method} --dist ${dist_func} ${common_params}"
	done
done

for dist_func in "${dist_funcs[@]}"
do
    echo "python gen_candidate_trees.py --method lst --dist ${dist_func} --dij  ${common_params}"
done
