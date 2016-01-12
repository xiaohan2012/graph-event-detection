#! /bin/bash
methods=(variance lst greedy random)
sampling_methods=(uniform)

for method in "${methods[@]}"; do
	for sampling_method in "${sampling_methods[@]}"; do
		python gen_candidate_trees.py \
			--method=${method} \
			--root_sampling=${sampling_method} \
			--seconds=8 --U=0.5 \
			--dist=euclidean \
			--cand_n=-1 \
			--res_dir=tmp/synthetic \
			--lda_path=None \
			--corpus_dict_path=None \
			--interaction_path=data/synthetic/interactions.json \
			--meta_graph_path_prefix=tmp/synthetic/meta-graph \
		        --given_topics
	done
done
