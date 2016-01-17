#! /bin/bash
Us=(0.5 1.0 1.5 2.0 2.5 3.0 3.5 4.0 4.5 5.0 5.5 6.0 6.5 7.0 7.5 8.0 8.5 9.0 9.5 10.0)

interaction_path=$2

if [ -z "$interaction_path" ];then
    echo "'interaction_path' as \$2"
    exit -1
fi

if [ $1 == 'mg' ]; then
	python gen_candidate_trees.py \
		--method=lst \
		--root_sampling=uniform \
		--seconds=8 \
		--U=0 \
		--dist=euclidean \
		--cand_n=0 \
	        --cand_n_percent=0 \
		--result_prefix=tmp/synthetic/result- \
		--lda_path=None \
		--corpus_dict_path=None \
		--interaction_path=${interaction_path} \
		--meta_graph_path_prefix=tmp/synthetic/U/meta-graph \
		--given_topics \
		--calc_mg
fi

if [ $1 == 'gen' ]; then
    methods=("lst --dij" "greedy" "random")  # "variance" "variance --dij"  "lst"
    for U in "${Us[@]}"; do
		for method in "${methods[@]}"; do
			python gen_candidate_trees.py \
				--method=${method} \
				--root_sampling=out_degree \
				--seconds=8 --U=${U} \
				--dist=euclidean \
				--cand_n_percent=0.1 \
				--result_prefix=tmp/synthetic/U/result- \
				--lda_path=None \
				--corpus_dict_path=None \
				--interaction_path=${interaction_path} \
				--meta_graph_path_prefix=tmp/synthetic/U/meta-graph \
				--given_topics
		done
    done
fi
