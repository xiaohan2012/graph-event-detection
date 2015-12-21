#! /bin/bash

if [ -z $1 ]; then
	echo "events pickle dir is not given"
	exit -1
fi

pickle_dir=$1
for p in $(ls $pickle_dir); do
	python dump_events_to_json.py ${pickle_dir}/${p} html/data
done

cd html
python ../dump_all_events_paths.py data > data/all_results.json
cd ..
