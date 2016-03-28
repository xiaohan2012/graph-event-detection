#! /bin/bash

root_dir='/cs/home/hxiao/code/lst'

dataset=$1
U=$2
cand_n=$3

# sampler="random"
sampler="adaptive"

# CMD="kernprof -l "
CMD="python"

if [ -z $1 ]; then
	echo "'dataset' required as \$1"
	exit -1
fi

if [ -z $2 ]; then
	echo "'U' required as \$2"
	exit -1
fi

if [ -z $3 ]; then
	echo "'cand_n' required as \$3"
	exit -1
fi

extra=$4

if [ ! -d ${root_dir}/tmp/${dataset} ]; then
    mkdir -p ${root_dir}/tmp/${dataset}
fi

time ${CMD} gen_candidate_trees.py \
	--method=greedy \
	--root_sampling=${sampler} \
	--dist=cosine \
	--result_prefix=${root_dir}/tmp/${dataset}/result- \
        --all_paths_pkl_prefix=${root_dir}/tmp/${dataset}/paths- \
	--lda_path=$(ls ${root_dir}/data/${dataset}/model-*.lda) \
	--corpus_dict_path=${root_dir}/data/${dataset}/dict.pkl \
	--interaction_path=${root_dir}/data/${dataset}/interactions.json \
	--meta_graph_path_prefix=${root_dir}/tmp/${dataset}/meta-graph \
	--U=${U} \
        --cand_n=${cand_n} \
	${extra}

