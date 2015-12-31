#! /bin/bash
# Example:
# ./scripts/make_d3_contexted_events_data.sh tmp/lda-25-topics/ data/enron.json 

if [ -z $1 ]; then
	echo "events pickle dir is not given"
	exit -1
fi

if [ -z $2 ]; then
	echo "interaction json path is not given"
	exit -1
fi

pickle_dir=$1
interactions_path=$2

for p in $(ls $pickle_dir); do
	echo "${p}"
	python dump_contexted_events_to_json.py ${interactions_path} ${pickle_dir}/${p} html/data
done

cd html
python ../dump_all_events_paths.py data > data/all_contexted_events_paths.json
cd ..
