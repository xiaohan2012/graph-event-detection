#! /bin/bash
Us=(0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1.0)

if [ $1 == 'mg' ]; then
	python gen_candidate_trees.py \
		--method=lst \
		--root_sampling=uniform \
		--seconds=8 \
		--U=0 \
		--dist=euclidean \
		--cand_n=-1 \
		--res_dir=tmp/synthetic \
		--lda_path=None \
		--corpus_dict_path=None \
		--interaction_path=data/synthetic/interactions.json \
		--meta_graph_path_prefix=tmp/synthetic/U/meta-graph \
		--given_topics \
		--calc_mg
fi

if [ $1 == 'gen' ]; then
	methods=(variance lst greedy random)
	for method in "${methods[@]}"; do
		for U in "${Us[@]}"; do
			python gen_candidate_trees.py \
				--method=${method} \
				--root_sampling=uniform \
				--seconds=8 --U=${U} \
				--dist=euclidean \
				--cand_n=-1 \
				--res_dir=tmp/synthetic/U/result- \
				--lda_path=None \
				--corpus_dict_path=None \
				--interaction_path=data/synthetic/interactions.json \
				--meta_graph_path_prefix=tmp/synthetic/U/meta-graph \
				--given_topics
		done
	done
fi
