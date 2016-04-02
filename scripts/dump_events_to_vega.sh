#! /bin/bash

if [ -z $1 ]; then
	echo 'ds not given'
	exit -1
fi

dataset=$1

output_dir=/cs/home/hxiao/public_html/event_html/data/${dataset}/vega

if [ ! -d ${output_dir} ]; then
	mkdir ${output_dir}
fi

python  dump_events_to_vega_format.py \
	--result_path tmp/${dataset}/result*.pkl \
	--interactions_path data/${dataset}/interactions.json \
	--output_path ${output_dir}/data.json \
	--k 5 \
	# --non_event_sample_n 1000 \


chmod -R a+rx ${output_dir}
