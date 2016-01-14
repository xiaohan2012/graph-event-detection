#! /bin/bash
timespans=(2 4 6 8 10 12 14 16 18 20 22 24 26 30)

if [ $1 == 'mg' ]; then
	for ts in "${timespans[@]}"; do
		python gen_candidate_trees.py \
			--method=lst \
			--root_sampling=uniform \
			--seconds=${ts} \
			--U=0 \
			--dist=euclidean \
			--cand_n=0 \
			--cand_n_percent=0 \
			--result_prefix=tmp/synthetic/result- \
			--lda_path=None \
			--corpus_dict_path=None \
			--interaction_path=data/synthetic/interactions.json \
			--meta_graph_path_prefix=tmp/synthetic/preprune_seconds/meta-graph-${ts} \
			--given_topics \
			--calc_mg
	done
fi

if [ $1 == 'gen' ]; then
    method="greedy"
	percent=0.2
	sampling="out_degree"
	U=0.5
	for ts in "${timespans[@]}"; do
		python gen_candidate_trees.py \
			--method=${method} \
			--root_sampling=${sampling} \
			--seconds=${ts} \
			--U=${U} \
			--dist=euclidean \
			--cand_n_percent=${percent} \
			--result_prefix=tmp/synthetic/preprune_seconds/result- \
			--lda_path=None \
			--corpus_dict_path=None \
			--interaction_path=data/synthetic/interactions.json \
			--meta_graph_path_prefix=tmp/synthetic/preprune_seconds/meta-graph-${ts} \
			--given_topics
	done
fi
