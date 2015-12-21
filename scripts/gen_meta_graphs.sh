#! /bin/bash

common="--lda=models/model-25-100.lda --weeks=8 --res_dir=tmp/lda-25-topics"

python gen_candidate_trees.py --dist cosine --calc_mg --cand_n 0 --method random ${common}
python gen_candidate_trees.py --dist euclidean --calc_mg --cand_n 0 --method random  ${common}
