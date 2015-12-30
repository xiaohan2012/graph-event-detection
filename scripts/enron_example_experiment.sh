#! /bin/bash

python gen_candidate_trees.py --method lst --dist euclidean --U=5 --weeks=4 --lda_path=models/model-25-100.lda --res_dir=tmp/enron/ --interaction_path=data/enron.json --corpus_dict_path=models/dictionary.pkl --meta_graph_path_prefix=tmp/enron/meta-graph --fixed_point=1 --cand_n=5\
 # --calc_mg
