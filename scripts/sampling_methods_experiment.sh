#! /bin/bash

export root_dir='/cs/home/hxiao/code/lst'
export dir_suffix="-sampling-scheme-experiment"

PARALLEL="/cs/home/hxiao/.local/bin/parallel --tmpdir /cs/home/hxiao/tmp "

if [ -z $1 ]; then
    echo "'dataset' required as \$1"
    exit -1
fi

if [ -z $2 ]; then
    echo "'operation' required as \$2"
    exit -1
fi

operation=$2

export dataset=$1

echo "using dataset '${dataset}'"


# How to set the following parameters?
U=15.0
n_events=10

data_dir="${root_dir}/data/${dataset}${dir_suffix}"
result_dir="${root_dir}/tmp/${dataset}${dir_suffix}"


samplers=("random" "upperbound" "adaptive")

if [ "${operation}" == "gen" ]; then
    n_sampled_roots=100

    if [ ! -d ${root_dir}/tmp/${dataset}${dir_suffix} ]; then
	mkdir -p ${root_dir}/tmp/${dataset}${dir_suffix}
    else
	rm ${root_dir}/tmp/${dataset}${dir_suffix}/result-*
	rm ${root_dir}/tmp/${dataset}${dir_suffix}/path-*
    fi

    function run_experiment {
	if [ -z $1 ]; then
	    echo 'method should be given'
	    exit -1
	fi

	if [ -z $2 ]; then
	    echo 'cand_n should be given'
	    exit -1
	fi

	python gen_candidate_trees.py \
	    --method=greedy \
	    --root_sampling=$1 \
	    --dist=cosine \
	    --result_prefix=${root_dir}/tmp/${dataset}${dir_suffix}/result- \
            --all_paths_pkl_prefix=${root_dir}/tmp/${dataset}${dir_suffix}/paths- \
	    --lda_path=$(ls ${root_dir}/data/${dataset}/model-*.lda) \
	    --corpus_dict_path=${root_dir}/data/${dataset}/dict.pkl \
	    --interaction_path=${root_dir}/data/${dataset}/interactions.json \
	    --meta_graph_path_prefix=${root_dir}/tmp/${dataset}${dir_suffix}/meta-graph \
	    --U=15.0 \
            --cand_n=$2 \
	    --days=1 \
            --random_seed 123456 \
	    --weight_for_topics=0.4 \
	    --weight_for_hashtag_bow=0.4 \
	    --weight_for_bow=0.2
	    # --weight_for_topics=0.8 \
	    # --weight_for_bow=0.2 
    }


    export -f run_experiment

    echo "generating the meta graph..."
    run_experiment random 1 # gen the metagraph

    # rm the result
    rm ${root_dir}/tmp/${dataset}${dir_suffix}/result-*
    rm ${root_dir}/tmp/${dataset}${dir_suffix}/paths-*

    ${PARALLEL} run_experiment ::: ${samplers[@]} ::: ${n_sampled_roots}
fi


eval_result_path=${result_dir}/eval_result.pk

if [ "${operation}" == "eval" ]; then
    python sampler_evaluation.py \
	--experiment_paths ${result_dir}/paths*.pkl \
	--legends "${samplers[@]}" \
	-k ${n_events} \
	--metrics k_setcover_obj \
	--output_path ${eval_result_path}
fi

if [ "${operation}" == "viz" ]; then
    if [ ! -d ${result_dir}/figure/ ]; then
	mkdir -p ${result_dir}/figure/
    fi
    python draw_evaluation_result.py \
	--result_path ${eval_result_path} \
	--xlabel "#epoch" \
	--output_dir ${result_dir}/figure/
    ssh shell.cs.helsinki.fi mkdir -p /cs/home/hxiao/public_html/figures/${dataset}${dir_suffix}
    scp ${result_dir}/figure/*  shell.cs.helsinki.fi:/cs/home/hxiao/public_html/figures/${dataset}${dir_suffix}
fi
