#! /bin/bash

fractions=(0.2 0.4 0.6 0.8 1.0 1.2 1.4 1.6 1.8 2.0 2.2 2.4 2.6 2.8 3.0)
method=greedy
U=0.5
seconds=8
percent=0.5

if [ "$1" == "data" ]; then
	for fraction in "${fractions[@]}"; do
		echo "fraction: ${fraction}"
		python artificial_data.py \
			--n_noisy_interactions_fraction ${fraction} \
			--output_dir tmp/synthetic/noise_fraction/data
	done
fi

if [ "$1" == "run" ]; then
	for fraction in "${fractions[@]}"; do
		echo "fraction: ${fraction}"
		res_dir=tmp/synthetic/result/fraction-${fraction}
		if [ ! -d ${res_dir} ]; then
			mkdir -p ${res_dir}
		fi

		python gen_candidate_trees.py \
			--method=${method} \
			--root_sampling=out_degree \
			--seconds=${seconds} \
			--U=${U} \
			--dist=euclidean \
			--cand_n_percent ${percent} \
			--res_dir=${res_dir} \
			--lda_path=None \
			--corpus_dict_path=None \
			--interaction_path=tmp/synthetic/noise_fraction/data/interactions--n_noisy_interactions_fraction=${fraction}.json \
			--meta_graph_path_prefix=${res_dir}/meta-graph \
		    --given_topics \
			--calc_mg
	done
fi
