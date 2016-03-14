#! /bin/bash

fraction=5.0
n_events=5
methods=("random" "upperbound" "adaptive")
# methods=("adaptive")

U=3.2

data_dir='/home/hxiao/code/lst_dag/data/synthetic_sampling_methods'
result_dir='/home/hxiao/code/lst_dag/tmp/synthetic_sampling_methods'


if [ "$1" == "data" ]; then
	rm -r ${data_dir}/*

	if [ ! -d "${data_dir}" ]; then
		mkdir -p "${data_dir}"
	fi
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
		--alpha 0.5
fi

if [ "$1" == "gen" ]; then
	rm -r ${result_dir}/*

	result_paths=()
	for method in "${methods[@]}"; do
		result_prefix=${result_dir}/result/result--fraction=${fraction}--
		if [ ! -d "${result_dir}/result" ]; then
			mkdir -p "${result_dir}/result"
		fi

		python gen_candidate_trees.py \
			--method=greedy \
			--U ${U} \
			--dist=cosine \
			--lda_path=None \
			--corpus_dict_path None \
			--interaction_path ${data_dir}/interactions--n_noisy_interactions_fraction=${fraction}.json \
			--meta_graph_path_prefix ${result_dir}/meta-graph \
			--result_prefix=${result_prefix} \
			--given_topics \
			--weight_for_bow 0 \
			--weight_for_topics 1.0 \
			--not_convert_time \
			--time_diff_unit sec \
			--cand_n_percent 0.20 \
			--seconds 50 \
			--root_sampling ${method}

		result_paths=("${result_paths[@]}" "$(python read_result_path.py)")
	done
	python sampler_evaluation.py \
		--result_paths "${result_paths[@]}" \
		--legends "${methods[@]}" \
		-k ${n_events} \
		--true_trees_path ${data_dir}/gen_cand_tree_params--n_noisy_interactions_fraction=${fraction}.pkl \
		--output_path /cs/home/hxiao/public_html/figures/sampling_methods/result.png

	chmod -R a+rx /cs/home/hxiao/public_html/figures/sampling_methods/

fi
