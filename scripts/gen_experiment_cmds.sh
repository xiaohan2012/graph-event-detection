#! /bin/bash

decompose=$1

methods=("lst" "greedy" "random")
dist_funcs=("euclidean")
U=(1 2 5)
weeks=(2 4 8)

common_params="--lda=models/model-25-100.lda --res_dir=tmp/lda-25-topics --fixed_point=1"

for dist_func in "${dist_funcs[@]}"
do
    for u in "${U[@]}"
    do
	for w in "${weeks[@]}"
	do
	    sub_common="--dist ${dist_func} --U=${u} --weeks=${w}"
	    for method in "${methods[@]}"
	    do		
		base="python gen_candidate_trees.py --method ${method} ${sub_common}  ${common_params}"
		echo $base
		if [[ $decompose == 'd' ]]; then
		    echo "${base} --decompose"		
		fi
	    done
	    # with dijkstra
	    base="python gen_candidate_trees.py --method lst --dij ${sub_common} ${common_params}"
	    echo $base
	    if [[ $decompose == 'd' ]]; then
			echo "${base} --decompose"
	    fi
	done
    done
done
