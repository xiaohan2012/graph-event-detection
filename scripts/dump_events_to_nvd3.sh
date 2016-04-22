#! /bin/bash

if [ -z $1 ]; then
	echo 'ds not given'
	exit -1
fi

dataset=$1

output_dir=/cs/home/hxiao/public_html/event_html/data/${dataset}/nvd3

if [ ! -d ${output_dir} ]; then
	mkdir ${output_dir}
fi

if [ ${dataset} == "enron_small" ]; then
	extra="--freq 1w --k 10"
elif [ ${dataset} == "letter" ]; then
	extra="--freq 12m --k 10"
elif [[ ${dataset} == nba* ]]; then
	extra="--freq 5Min --k 10 --non_event_sample_n 1000"
else
	extra="--non_event_sample_n 5000 --freq 1h --k 5"
fi

echo "$extra"

python  dump_events_to_nvd3.py \
	--result_path tmp/${dataset}/result*.pkl \
	--interactions_path data/${dataset}/interactions.* \
	--output_path ${output_dir}/data.json \
	${extra}


chmod -R a+rx ${output_dir}
