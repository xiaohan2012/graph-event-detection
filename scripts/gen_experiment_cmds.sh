#! /bin/bash

methods=("lst" "greedy" "random")
dist_funcs=("euclidean")
U=(0.01 0.1 1 2)

common_params="--lda=models/model-25-100.lda --weeks=8 --res_dir=tmp/lda-25-topics"

for dist_func in "${dist_funcs[@]}"
do
	for method in "${methods[@]}"
	do
		for u in "${U[@]}"
		do
			echo "python gen_candidate_trees.py --method ${method} --dist ${dist_func} --U=${u} ${common_params}"
		done
	done
done

for u in "${U[@]}"
do
	for dist_func in "${dist_funcs[@]}"
	do
		echo "python gen_candidate_trees.py --method lst --dist ${dist_func} --dij --U=${u}  ${common_params}"
	done
done
