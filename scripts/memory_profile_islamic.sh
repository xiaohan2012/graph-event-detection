#! /bin/bash

CURDIR=/home/hxiao/code/lst_dag

python -m memory_profiler gen_candidate_trees.py --dist euclidean --calc_mg --cand_n 0 --method random --lda_path="${CURDIR}/data/islamic/model-100-50.lda" --weeks=2 --res_dir="${CURDIR}/tmp/islamic/" --interaction_path="${CURDIR}/tmp/islamic-head-5000.json" --corpus_dict_path="${CURDIR}/data/islamic/dict.pkl" --meta_graph_path_prefix="${CURDIR}/tmp/islamic/meta-graph"
