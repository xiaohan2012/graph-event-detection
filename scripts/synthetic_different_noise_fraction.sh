#! /bin/bash

rounds=50

export methods=("random" "greedy" "lst" "lst+dij" "quota")
export data_dir='/cs/home/hxiao/code/lst/data/synthetic_noise'
export result_dir='/cs/home/hxiao/code/lst/tmp/synthetic_noise'

export fraction_start=0.0
export fraction_step=2.5
export fraction_end=100.0

PARALLEL="/cs/home/hxiao/.local/bin/parallel --tmpdir /cs/home/hxiao/tmp "
SINGLE_ROUND_SCRIPT="./scripts/synthetic_comparing_algorithms_against_noise.sh"

export extra=''

export rounds_array=$(seq 1 1 ${rounds})

echo "Rounds: ${rounds}"

if [ "$1" == "data" ]; then
    if [ ! -d ${data_dir} ]; then
	mkdir -p ${data_dir}
    else
	rm -r ${data_dir}/*
    fi

    function gen_data(){
	round=$1
	fraction=$2

	if [ -z $1 ]; then
	    echo '\$1 as round missing'
	    exit -1
	fi
	if [ -z $2 ]; then
	    echo '\$2 as fraction missing'
	    exit -1
	fi  

	python artificial_data.py \
	    --n_events 1 \
	    --event_size_mu 20 \
	    --event_size_sigma 1 \
	    --participant_mu 4 \
	    --participant_sigma 0.1 \
	    --n_total_participants 25 \
	    --min_time 10 \
	    --max_time  51 \
	    --event_duration_mu 50 \
	    --n_topics 10 \
	    --n_noisy_interactions_fraction ${fraction} \
	    --topic_noise 1.0 \
	    --topic_scaling_factor 10.0 \
	    --output_dir ${data_dir} \
	    --result_suffix "-${round}" \
	    ${extra}
    }
    
    export -f gen_data
    ${PARALLEL} gen_data ::: ${rounds_array[@]} ::: $(seq ${fraction_start} ${fraction_step} ${fraction_end})
fi

if [ "$1" == "gen" ]; then
    if [ -d ${result_dir} ]; then
	rm -r ${result_dir}/*
    fi

    mkdir -p "${result_dir}/paths"
    mkdir -p "${result_dir}/result"

    function gen_cand_tree(){
	round=$1
	method=$2
	fraction=$3

	if [ -z $1 ]; then
	    echo '\$1 as round missing'
	    exit -1
	fi
	if [ -z $2 ]; then
	    echo '\$2 as method missing'
	    exit -1
	fi
	if [ -z $3 ]; then
	    echo '\$3 as fraction missing'
	    exit -1
	fi  

	result_prefix=${result_dir}/result/result--fraction=${fraction}--
	path_file_prefix=${result_dir}/paths/fraction=${fraction}--

	python gen_candidate_trees.py \
	    --method=${method} \
	    --dist=cosine \
	    --lda_path=None \
	    --corpus_dict_path None \
	    --interaction_path ${data_dir}/interactions--*n_noisy_interactions_fraction=${fraction}-${round}.json \
	    --event_param_pickle_path ${data_dir}/gen_cand_tree_params--*n_noisy_interactions_fraction=${fraction}-${round}.pkl \
	    --meta_graph_path_prefix ${result_dir}/meta-graph--fraction=${fraction} \
	    --result_prefix ${result_prefix} \
	    --all_paths_pkl_prefix ${path_file_prefix} \
	    --all_paths_pkl_suffix "-${round}" \
	    --meta_graph_pkl_suffix "-${round}" \
	    --result_suffix "-${round}" \
	    --true_events_path ${data_dir}/events--*n_noisy_interactions_fraction=${fraction}-${round}.pkl \
	    --given_topics \
	    --weight_for_bow 0 \
	    --weight_for_topics 1.0 \
	    --not_convert_time \
	    ${extra}
    }
    export -f gen_cand_tree
    ${PARALLEL} gen_cand_tree ::: ${rounds_array[@]} ::: ${methods[@]} ::: $(seq ${fraction_start} ${fraction_step} ${fraction_end})
fi

combined_eval_result_path=${result_dir}/eval/combined.pkl

if [ "$1" == "eval" ]; then
    if [ ! -d ${result_dir}/eval/ ]; then
	mkdir -p ${result_dir}/eval/
    fi

    function eval_result(){
	if [ -z $1 ]; then
	    echo '\$1 as round missing'
	    exit -1
	fi
	round=$1
	python synthetic_evaluation.py \
	    --experiment_paths ${result_dir}/paths/*-${round}.pkl \
	    --output_path ${result_dir}/eval/eval_result-${round}.pkl \
	    --xticks $(seq ${fraction_start} ${fraction_step} ${fraction_end}) \
	    --experiment noise
    }

    export -f eval_result
    ${PARALLEL} eval_result ::: ${rounds_array[@]}
    
    echo ${combined_eval_result_path}
	# combine
    python combine_evaluation_results.py \
	--result_paths ${result_dir}/eval/eval_result*.pkl \
	--output_path ${combined_eval_result_path}
fi


if [ "$1" == "viz" ]; then
    if [ ! -d ${result_dir}/figure ]; then
	mkdir -p ${result_dir}/figure
    fi
	# viz
    python draw_evaluation_result.py \
	--result_path ${combined_eval_result_path} \
	--xlabel "noise fraction" \
	--output_dir ${result_dir}/figure
    scp ${result_dir}/figure/*  shell.cs.helsinki.fi:/cs/home/hxiao/public_html/figures/synthetic/noise_fraction/
fi
