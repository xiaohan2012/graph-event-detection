#! /bin/bash

methods=("random" "greedy" "quota" "lst --dij")

data_dir='/cs/home/hxiao/code/lst_dag/data/synthetic_single_tree'
result_dir='/cs/home/hxiao/code/lst_dag/tmp/synthetic_single_tree'

ALPHA=0.5
TAU=0.8

extra=''

fraction_start=0.5
fraction_step=0.5
fraction_end=10.0


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
	if [ ! -d ${data_dir} ]; then
		mkdir -p ${data_dir}
	fi
	rm -r ${data_dir}/*
	echo "time: ${round}"
	for fraction in $(seq ${fraction_start} ${fraction_step} ${fraction_end}); do
		# for fraction in "${fractions[@]}"; do
		echo "fraction: ${fraction}"
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
			--n_topics 5 \
			--n_noisy_interactions_fraction ${fraction} \
			--topic_noise 1.0 \
			--topic_scaling_factor 10.0 \
			--output_dir ${data_dir} \
			--alpha 0.5 \
			--edge_cost_alpha ${ALPHA} \
			--edge_cost_tau ${TAU} \
			--result_suffix "-${round}" \
			${extra}
	done
fi

if [ ${operation} == "gen" ]; then
	rm -r ${result_dir}/*

	for method in "${methods[@]}"; do
		for fraction in $(seq ${fraction_start} ${fraction_step} ${fraction_end}); do
			echo "fraction: ${fraction}"
			result_prefix=${result_dir}/result/result--fraction=${fraction}--
			path_file_prefix=${result_dir}/paths/fraction=${fraction}--

			if [ ! -d "${result_dir}/paths" ]; then
				mkdir -p "${result_dir}/paths"
			fi

			if [ ! -d "${result_dir}/result" ]; then
				mkdir -p "${result_dir}/result"
			fi

			python gen_candidate_trees.py \
				--method=${method} \
				--dist=cosine \
				--lda_path=None \
				--corpus_dict_path None \
				--interaction_path ${data_dir}/interactions--n_noisy_interactions_fraction=${fraction}-${round}.json \
				--event_param_pickle_path ${data_dir}/gen_cand_tree_params--n_noisy_interactions_fraction=${fraction}-${round}.pkl \
				--meta_graph_path_prefix ${result_dir}/meta-graph--fraction=${fraction} \
				--result_prefix ${result_prefix} \
				--all_paths_pkl_prefix ${path_file_prefix} \
				--all_paths_pkl_suffix "-${round}" \
				--meta_graph_pkl_suffix "-${round}" \
				--result_suffix "-${round}" \
				--true_events_path ${data_dir}/events--n_noisy_interactions_fraction=${fraction}-${round}.pkl \
				--given_topics \
				--weight_for_bow 0 \
				--weight_for_topics 1.0 \
				--not_convert_time \
				--alpha ${ALPHA} \
				--tau ${TAU} \
				--time_diff_unit sec \
				${extra}
		done
	done
fi

if [ ${operation} == "eval" ]; then
	if [ ! -d ${result_dir}/eval/ ]; then
		mkdir -p ${result_dir}/eval/
	fi

	# evaluate
	python synthetic_evaluation.py \
		--experiment_paths ${result_dir}/paths/*-${round}.pkl \
		--output_path ${result_dir}/eval/eval_result-${round}.pkl
	
fi

