#! /bin/bash

methods=("lst" "greedy" "random")
dist_funcs=("euclidean" "cosine")

for method in "${methods[@]}"
do    
  for dist_func in "${dist_funcs[@]}"
  do
      echo "python gen_candidate_trees.py --method ${method} --dist ${dist_func}"
  done
done

for dist_func in "${dist_funcs[@]}"
do
    echo "python gen_candidate_trees.py --method lst --dist ${dist_func} --dij"
done