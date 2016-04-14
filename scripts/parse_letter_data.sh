#! /bin/bash

HOME='/cs/home/hxiao'

python letter_parser.py \
	--data_dir "${HOME}/Downloads/letters/*.txt" \
	--output_path "${HOME}/code/lst/data/letter/interactions.pkl"
