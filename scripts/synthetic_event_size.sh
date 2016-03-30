#! /bin/bash

rounds=50
# rounds=2

PARALLEL="/cs/home/hxiao/.local/bin/parallel --tmpdir /cs/home/hxiao/tmp "
SINGLE_ROUND_SCRIPT="./scripts/synthetic_comparing_algorithms_against_event_size.sh"

export data_dir='/cs/home/hxiao/code/lst/data/synthetic_event_size'
export result_dir='/cs/home/hxiao/code/lst/tmp/synthetic_event_size'

export methods=("random" "greedy" "lst+dij" "quota")

event_size_start=10
event_size_step=5
event_size_end=100

# event_size_start=10
# event_size_step=5
# event_size_end=15

export event_sizes=$(seq ${event_size_start} ${event_size_step} ${event_size_end})

export fraction=5.0

rounds_array=$(seq 1 1 ${rounds})

echo "Rounds: ${rounds}"

if [ "$1" == "data" ]; then
    if [ ! -d ${data_dir} ]; then
	mkdir -p ${data_dir}
    else
	rm -r ${data_dir}/*
    fi

    function gen_data(){
	if [ -z $1 ]; then
	    exit -1
	fi
	if [ -z $2 ]; then
	    exit -1
	fi
	round=$1
	event_size=$2

	python artificial_data.py \
	    --n_events 1 \
	    --event_size_mu ${event_size} \
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
	    --result_suffix "-${round}"
    }
    export -f gen_data
    ${PARALLEL} gen_data  ::: ${rounds_array[@]} ::: ${event_sizes[@]}
fi

if [ "$1" == "gen" ]; then
    if [ -d ${result_dir} ]; then
	rm -r ${result_dir}/*
    fi
    function gen_tree(){
	if [ -z $1 ]; then
	    exit -1
	fi
	if [ -z $2 ]; then
	    exit -1
	fi
	if [ -z $3 ]; then
	    exit -1
	fi
	round=$1
	event_size=$2
	method=$3

	result_prefix=${result_dir}/result/result--event_size=${event_size}--
	path_file_prefix=${result_dir}/paths/event_size=${event_size}
	exp_sig="event_size=${event_size}--n_noisy_interactions_fraction=${fraction}"

	python gen_candidate_trees.py \
	    --method=${method} \
	    --dist=cosine \
	    --lda_path=None \
	    --corpus_dict_path None \
	    --interaction_path ${data_dir}/interactions--${exp_sig}-${round}.json \
	    --event_param_pickle_path ${data_dir}/gen_cand_tree_params--${exp_sig}-${round}.pkl \
	    --meta_graph_path_prefix ${result_dir}/meta-graph--event_size=${event_size} \
	    --result_prefix ${result_prefix} \
	    --all_paths_pkl_prefix ${path_file_prefix} \
	    --all_paths_pkl_suffix "-${round}" \
	    --meta_graph_pkl_suffix "-${round}" \
	    --result_suffix "-${round}" \
	    --true_events_path ${data_dir}/events--${exp_sig}-${round}.pkl \
	    --given_topics \
	    --weight_for_bow 0 \
	    --weight_for_topics 1.0 \
	    --not_convert_time

    }
    export -f gen_tree
    mkdir -p "${result_dir}/paths"
    mkdir -p "${result_dir}/result"

    ${PARALLEL} gen_tree ::: ${rounds_array[@]} ::: ${event_sizes[@]} ::: ${methods[@]}
fi

combined_eval_result_path=${result_dir}/eval/combined.pkl

if [ "$1" == "eval" ]; then
    if [ ! -d ${result_dir}/eval/ ]; then
	mkdir -p ${result_dir}/eval/
    fi

    function eval_result(){
	if [ -z $1 ]; then
	    exit -1
	fi
	round=$1
	python synthetic_evaluation.py \
	    --experiment_paths ${result_dir}/paths/*-${round}.pkl \
	    --output_path ${result_dir}/eval/eval_result-${round}.pkl \
	    --experiment event_size \
	    --xticks ${event_sizes[@]}
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
	--xlabel "event size" \
	--subplot_ordering precision recall f1 set_cover_obj "log(running_time)" \
	--output_dir ${result_dir}/figure
    scp ${result_dir}/figure/*  shell.cs.helsinki.fi:/cs/home/hxiao/public_html/figures/synthetic/event_size/
fi
