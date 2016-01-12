#! /bin/bash

dataset=$1

if [ -z $1 ]; then
	echo "'dataset' required as \$1"
	exit -1
fi


python gen_candidate_trees.py \
	--method=lst \
	--root_sampling=uniform \
	--seconds=8 \
	--U=0.5 \
	--dist=euclidean \
	--cand_n=0 \
	--res_dir=tmp/${dataset}/ \
	--lda_path=$(ls data/${dataset}/model-*.lda) \
	--corpus_dict_path=data/${dataset}/dict.pkl \
	--interaction_path=data/${dataset}/interactions.json \
	--meta_graph_path_prefix=tmp/${dataset}/meta-graph \
	--calc_mg

