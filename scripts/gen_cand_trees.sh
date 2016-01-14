#! /bin/bash

dataset=$1
U=$2
cand_n_percent=$3

if [ -z $1 ]; then
	echo "'dataset' required as \$1"
	exit -1
fi

if [ -z $2 ]; then
	echo "'U' required as \$2"
	exit -1
fi

if [ -z $3 ]; then
	echo "'cand_n_percent' required as \$3"
	exit -1
fi

extra=$4

time python gen_candidate_trees.py \
	--method=greedy \
	--root_sampling=out_degree \
	--weeks=2 \
	--dist=euclidean \
	--result_prefix=tmp/${dataset}/result- \
	--lda_path=$(ls data/${dataset}/model-*.lda) \
	--corpus_dict_path=data/${dataset}/dict.pkl \
	--interaction_path=data/${dataset}/interactions.json \
	--meta_graph_path_prefix=tmp/${dataset}/meta-graph \
	--U=${U} \
        --cand_n_percent=${cand_n_percent} \
	${extra}

