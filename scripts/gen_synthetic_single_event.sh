#! /bin/bash

python artificial_data.py \
	--n_events 1 \
	--event_size_mu 100 \
	--n_total_participants 10 \
	--participant_mu 10 \
	--min_time 10 \
	--max_time 110 \
	--event_duration_mu 10 \
	--n_topics 10 \
	--n_noisy_interactions 100 \
	--output_dir data/single_synthetic_event
