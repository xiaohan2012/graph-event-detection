#! /bin/bash

rounds=50

PARALLEL="/cs/home/hxiao/.local/bin/parallel --tmpdir /cs/home/hxiao/tmp "
SINGLE_ROUND_SCRIPT="./scripts/synthetic_comparing_algorithms_against_event_size.sh"

data_dir='/cs/home/hxiao/code/lst/data/synthetic_event_size'
result_dir='/cs/home/hxiao/code/lst/tmp/synthetic_event_size'

rounds_array=()
for ((round=1; round <= ${rounds}; round++)); do
    rounds_array=("${rounds_array[@]}" ${round})
done

echo "Rounds: ${rounds}"

if [ "$1" == "data" ]; then
	if [ ! -d ${data_dir} ]; then
	    mkdir -p ${data_dir}
	else
	    rm -r ${data_dir}/*
	fi

	${PARALLEL} ${SINGLE_ROUND_SCRIPT}  data ::: ${rounds_array[@]}
fi

if [ "$1" == "gen" ]; then
    if [ -d ${result_dir} ]; then
	rm -r ${result_dir}/*
    fi

    mkdir -p "${result_dir}/paths"
    mkdir -p "${result_dir}/result"


    ${PARALLEL} ${SINGLE_ROUND_SCRIPT} gen ::: ${rounds_array[@]}
fi

combined_eval_result_path=${result_dir}/eval/combined.pkl

if [ "$1" == "eval" ]; then
    if [ ! -d ${result_dir}/eval/ ]; then
	mkdir -p ${result_dir}/eval/
    fi

    ${PARALLEL} ${SINGLE_ROUND_SCRIPT} "eval" ::: ${rounds_array[@]}
    
    echo ${combined_eval_result_path}
	# combine
    python combine_evaluation_results.py \
	--result_paths ${result_dir}/eval/eval_result*.pkl \
	--output_path ${combined_eval_result_path}
fi


if [ "$1" == "viz" ]; then
    if [ ! -d ${result_dir}/figure ]; then
	mkdir -p ${result_dir}/figure
    fi
	# viz
    python draw_evaluation_result.py \
	--result_path ${combined_eval_result_path} \
	--xlabel "event size" \
	--output_dir ${result_dir}/figure
    scp ${result_dir}/figure/*  shell.cs.helsinki.fi:/cs/home/hxiao/public_html/figures/synthetic/event_size/
fi
