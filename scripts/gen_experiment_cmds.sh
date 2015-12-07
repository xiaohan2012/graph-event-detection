#! /bin/bash

methods=("lst" "greedy" "random")
dist_funcs=("entropy" "euclidean" "cosine")

for method in "${methods[@]}"
do    
  for dist_func in "${dist_funcs[@]}"
  do
      echo "python gen_candidate_trees.py ${method} ${dist_func}"
  done
done