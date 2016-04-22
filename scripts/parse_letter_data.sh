#! /bin/bash

python letter_parser.py \
	--data_dir "${HOME}/Downloads/letters-pos/*.pos" \
	--output_path "${HOME}/code/lst/data/letter/interactions.pkl"
