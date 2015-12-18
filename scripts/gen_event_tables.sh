#! /bin/bash

paths=("result-greedy--U=0.05--dijkstra=False--timespan=56days----decompose_interactions=False--dist_func=cosine.pkl" "result-lst--U=0.05--dijkstra=False--timespan=56days----decompose_interactions=False--dist_func=cosine.pkl"  "result-lst--U=0.05--dijkstra=True--timespan=56days----decompose_interactions=False--dist_func=cosine.pkl" "result-random--U=0.05--dijkstra=False--timespan=56days----decompose_interactions=False--dist_func=cosine.pkl")

for p in "${paths[@]}"
do
    echo $p
    python check_k_best_trees.py tmp/$p
	echo -e "\n"
done
