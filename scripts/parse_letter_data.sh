#! /bin/bash

HOME='/home/hxiao'

python letter_parser.py \
	--data_dir "${HOME}/Downloads/2510/PCEEC/corpus/txt/*" \
	--output_path "${HOME}/code/lst_dag/data/letter/interactions.json"
