#! /bin/bash

methods=("random" "greedy" "lst" "lst+dij" "quota")

event_size_start=10
event_size_step=5
event_size_end=100

fraction=1.0

operation=$1
round=$2

if [ -z $operation ]; then
    echo 'operation missing'
    exit -1
fi

if [ -z $round ]; then
    echo 'round missing'
    exit -1
fi

if [ ${operation} == "data" ]; then
    for event_size in $(seq ${event_size_start} ${event_size_step} ${event_size_end}); do
	echo "event_size: ${event_size}"
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
	    --result_suffix "-${round}" \
	    ${extra}
    done
fi

if [ ${operation} == "gen" ]; then
    for event_size in $(seq ${event_size_start} ${event_size_step} ${event_size_end}); do
	for method in "${methods[@]}"; do
	    echo "event_size: ${event_size}"
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
		--not_convert_time \
		${extra}
	done
    done
fi

if [ ${operation} == "eval" ]; then
    if [ ! -d ${result_dir}/eval/ ]; then
	mkdir -p ${result_dir}/eval/
    fi

    python synthetic_evaluation.py \
	--experiment_paths ${result_dir}/paths/*-${round}.pkl \
	--output_path ${result_dir}/eval/eval_result-${round}.pkl \
	--experiment event_size \
	--xticks $(seq ${event_size_start} ${event_size_step} ${event_size_end})
fi

