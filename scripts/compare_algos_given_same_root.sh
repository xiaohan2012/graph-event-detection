#! /bin/bash

root_dir='/cs/home/hxiao/code/lst'

roots=(572772702445940736)

if [ -z $1 ]; then
	echo "'dataset' required as \$1"
	exit -1
fi

export dataset=$1

function gen_tree(){
    time python gen_candidate_trees.py \
	--method=$1 \
	--root_sampling=random \
	--dist=cosine \
	--result_prefix=${root_dir}/tmp/${dataset}/result- \
        --all_paths_pkl_prefix=${root_dir}/tmp/${dataset}/paths- \
	--lda_path=$(ls ${root_dir}/data/${dataset}/model-*.lda) \
	--corpus_dict_path=${root_dir}/data/${dataset}/dict.pkl \
	--interaction_path=${root_dir}/data/${dataset}/interactions.json \
	--meta_graph_path_prefix=${root_dir}/tmp/${dataset}/meta-graph \
	--U=${2} \
	--roots=${3} \
	--weight_for_topics 0.4 \
	--weight_for_hashtag_bow 0.4 \
	--weight_for_bow 0.2 \
	--days 1
}

export -f gen_tree

methods=("greedy" "lst+dij" "quota")
for method in ${methods[@]}; do
    gen_tree ${method} 30.0 "${roots[@]}"
done