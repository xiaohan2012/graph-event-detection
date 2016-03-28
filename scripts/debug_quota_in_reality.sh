#! /bin/bash

export root_dir='/cs/home/hxiao/code/lst'
export dir_suffix="-budget-experiment"
export dataset=beefban

function run_experiment {
	if [ -z $1 ]; then
	    echo 'method should be given'
	    exit -1
	fi

	if [ -z $2 ]; then
	    echo 'U should be given'
	    exit -1
	fi

	if [ -z $3 ]; then
	    echo 'roots should be given'
	    exit -1
	fi

	python gen_candidate_trees.py \
	    --method=$1 \
	    --root_sampling=random \
	    --dist=cosine \
	    --result_prefix=${root_dir}/tmp/${dataset}-${dir_suffix}/result- \
            --all_paths_pkl_prefix=${root_dir}/tmp/${dataset}-${dir_suffix}/paths- \
	    --lda_path=$(ls ${root_dir}/data/${dataset}/model-*.lda) \
	    --corpus_dict_path=${root_dir}/data/${dataset}/dict.pkl \
	    --interaction_path=${root_dir}/data/${dataset}/interactions.json \
	    --meta_graph_path_prefix=${root_dir}/tmp/${dataset}-${dir_suffix}/meta-graph \
	    --U=$2 \
            --roots $3 \
	    --days=1 \
	    --weight_for_topics=0.4 \
	    --weight_for_hashtag_bow=0.4 \
	    --weight_for_bow=0.2 \
            --random_seed 123456
    }


export -f run_experiment

run_experiment quota 5.0 572718337978855426
