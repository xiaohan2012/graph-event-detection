#! /bin/bash

python gen_candidate_trees.py --dist cosine --calc_mg --cand_n 0 --method random
python gen_candidate_trees.py --dist euclidean --calc_mg --cand_n 0 --method random
