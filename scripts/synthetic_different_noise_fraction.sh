#! /bin/bash

# fractions=(0.2 0.4 0.6 0.8 1.0 1.2 1.4 1.6 1.8 2.0 2.2 2.4 2.6 2.8 3.0)
rounds=10
methods=("random" "greedy" "quota" "lst --dij")

data_dir='/home/hxiao/code/lst_dag/data/synthetic_single_tree'
result_dir='/home/hxiao/code/lst_dag/tmp/synthetic_single_tree'

ALPHA=0.5
TAU=0.8

# extra='--recency'
extra=''

fraction_start=0.5
fraction_step=0.5
fraction_end=5.0


if [ "$1" == "data" ]; then
	if [ ! -d ${data_dir} ]; then
		mkdir -p ${data_dir}
	fi
	rm -r ${data_dir}/*
	for ((round=1; round <= ${rounds}; round++)); do
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
	done
fi

if [ "$1" == "gen" ]; then
	rm -r ${result_dir}/*

	for ((round=1; round <= ${rounds}; round++)); do
		echo "time: ${round}"
		for method in "${methods[@]}"; do
			# for fraction in "${fractions[@]}"; do
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
					--meta_graph_pkl_suffix "-${round}" \
					--result_prefix ${result_prefix} \
					--result_suffix "-${round}" \
					--all_paths_pkl_prefix ${path_file_prefix} \
				    --all_paths_pkl_suffix "-${round}" \
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
	done

fi

combined_eval_result_path=${result_dir}/eval/combined.pkl

if [ "$1" == "eval" ]; then
	if [ ! -d ${result_dir}/eval/ ]; then
		mkdir -p ${result_dir}/eval/
	fi

	# evaluate
	for ((round=1; round <= ${rounds}; round++)); do
		python synthetic_evaluation.py \
			--experiment_paths ${result_dir}/paths/*-${round}.pkl \
			--output_path ${result_dir}/eval/eval_result-${round}.pkl
	done
	
	echo ${combined_eval_result_path}
	# combine
	python combine_evaluation_results.py \
		--result_paths ${result_dir}/eval/eval_result*.pkl \
		--output_path ${combined_eval_result_path}
fi

	
if [ "$1" == "viz" ]; then
	# viz
	python draw_evaluation_result.py \
		--result_path ${combined_eval_result_path} \
		--xlabel "noise fraction" \
		--output_dir /cs/home/hxiao/public_html/figures/synthetic/noise_fraction/
	chmod -R a+rx /cs/home/hxiao/public_html/figures/synthetic/noise_fraction/
fi
