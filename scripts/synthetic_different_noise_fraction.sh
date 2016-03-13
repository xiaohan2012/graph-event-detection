#! /bin/bash

# fractions=(0.2 0.4 0.6 0.8 1.0 1.2 1.4 1.6 1.8 2.0 2.2 2.4 2.6 2.8 3.0)
fractions=(0.0)
methods=("greedy")

data_dir='/home/hxiao/code/lst_dag/data/synthetic_single_tree'
result_dir='/home/hxiao/code/lst_dag/tmp/synthetic_single_tree'

ALPHA=0.5
TAU=0.8

extra='--recency'
# extra=''

if [ "$1" == "data" ]; then
	rm -r ${data_dir}/*
	for fraction in "${fractions[@]}"; do
		echo "fraction: ${fraction}"
		python artificial_data.py \
			--n_events 1 \
			--event_size_mu 20 \
			--event_size_sigma 1 \
			--participant_mu 4 \
			--participant_sigma 0.1 \
			--n_total_participants 20 \
			--min_time 10 \
			--max_time  100 \
			--event_duration_mu 50 \
			--n_topics 5 \
		    --n_noisy_interactions_fraction ${fraction} \
			--topic_noise 1.0 \
			--topic_scaling_factor 10.0 \
			--output_dir ${data_dir} \
			--alpha 0.5 \
			--edge_cost_alpha ${ALPHA} \
			--edge_cost_tau ${TAU} \
				${extra}
	done
fi

if [ "$1" == "gen" ]; then
	rm -r ${result_dir}/*
	for method in "${methods[@]}"; do
		for fraction in "${fractions[@]}"; do
			echo "fraction: ${fraction}"
			result_prefix=${result_dir}/result/result--fraction=${fraction}--
			if [ ! -d "${result_dir}/result" ]; then
				mkdir -p "${result_dir}/result"
			fi

			python gen_candidate_trees.py \
				--method=${method} \
				--dist=cosine \
				--lda_path=None \
				--corpus_dict_path None \
				--interaction_path ${data_dir}/interactions--n_noisy_interactions_fraction=${fraction}.json \
				--event_param_pickle_path ${data_dir}/gen_cand_tree_params--n_noisy_interactions_fraction=${fraction}.pkl \
				--meta_graph_path_prefix ${result_dir}/meta-graph \
				--result_prefix=${result_prefix} \
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
