#! /bin/bash

rounds=2
fraction=5.0
n_events=5
methods=("random" "upperbound" "adaptive")
# methods=("adaptive")

# How to set the following parameters?
U=3.2
timespan=50

data_dir='/home/hxiao/code/lst_dag/data/synthetic_sampling_methods'
result_dir='/home/hxiao/code/lst_dag/tmp/synthetic_sampling_methods'


if [ "$1" == "data" ]; then
	rm -r ${data_dir}/*

	if [ ! -d "${data_dir}" ]; then
		mkdir -p "${data_dir}"
	fi
	for ((round=1; round <= ${rounds}; round++)); do
		echo "round: ${round}"
		python artificial_data.py \
			--n_events ${n_events} \
			--event_size_mu 20 \
			--event_size_sigma 1 \
			--participant_mu 4 \
			--participant_sigma 0.1 \
			--n_total_participants 30 \
			--min_time 10 \
			--max_time  200 \
			--event_duration_mu 50 \
			--n_topics 10 \
			--n_noisy_interactions_fraction ${fraction} \
			--topic_noise 1.0 \
			--topic_scaling_factor 10.0 \
			--output_dir ${data_dir} \
			--alpha 0.5 \
			--result_suffix "-${round}"
	done
fi

if [ "$1" == "gen" ]; then
	rm -r ${result_dir}/*

	result_prefix=${result_dir}/result/
	if [ ! -d "${result_dir}/result" ]; then
		mkdir -p "${result_dir}/result"
	fi

	path_file_prefix=${result_dir}/paths/
	if [ ! -d "${result_dir}/paths" ]; then
		mkdir -p "${result_dir}/paths"
	fi

	for ((round=1; round <= ${rounds}; round++)); do
		echo "time: ${round}"
		for method in "${methods[@]}"; do
			python gen_candidate_trees.py \
				--method=greedy \
				--U ${U} \
				--dist=cosine \
				--lda_path=None \
				--corpus_dict_path None \
				--interaction_path ${data_dir}/interactions--n_noisy_interactions_fraction=${fraction}-${round}.json \
				--meta_graph_path_prefix ${result_dir}/meta-graph \
				--result_prefix ${result_prefix} \
				--all_paths_pkl_prefix ${path_file_prefix} \
				--true_events_path ${data_dir}/events--n_noisy_interactions_fraction=${fraction}-${round}.pkl \
				--all_paths_pkl_suffix "-${round}" \
				--meta_graph_pkl_suffix "-${round}" \
				--result_suffix "-${round}" \
				--given_topics \
				--weight_for_bow 0 \
				--weight_for_topics 1.0 \
				--not_convert_time \
				--time_diff_unit sec \
				--cand_n_percent 0.20 \
				--seconds ${timespan} \
				--root_sampling ${method}
		done
	done

fi


combined_eval_result_path=${result_dir}/eval/combined.pkl

if [ "$1" == "eval" ]; then
	if [ ! -d ${result_dir}/eval/ ]; then
		mkdir -p ${result_dir}/eval/
	fi

	for ((round=1; round <= ${rounds}; round++)); do
		echo "time: ${round}"
		python sampler_evaluation.py \
		--experiment_paths ${result_dir}/paths/*-${round}.pkl \
		--legends "${methods[@]}" \
		-k ${n_events} \
		--metrics k_setcover_obj precision recall f1 \
		--output_path ${result_dir}/eval/eval_result-${round}.pkl		
	done

	# combine
	python combine_evaluation_results.py \
		--result_paths ${result_dir}/eval/eval_result*.pkl \
		--output_path ${combined_eval_result_path}
fi

if [ "$1" == "viz" ]; then
	python draw_evaluation_result.py \
		--result_path ${combined_eval_result_path} \
		--xlabel "#epoch" \
		--output_dir /cs/home/hxiao/public_html/figures/sampling_methods
	chmod -R a+rx /cs/home/hxiao/public_html/figures/sampling_methods
fi
